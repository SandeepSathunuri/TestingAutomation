import os
import pandas as pd

class ExcelMerger:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    @staticmethod
    def merge_specific_files(file_paths, output_path, one_sheet=True):
        try:
            if not file_paths:
                print("⚠️ No files to merge.")
                return

            writer = pd.ExcelWriter(output_path, engine='openpyxl')
            print(f"📁 Merging files into: {output_path}")

            for file_path in file_paths:
                sheet_name = os.path.splitext(os.path.basename(file_path))[0][:31]
                df = pd.read_excel(file_path)

                if one_sheet:
                    df.to_excel(writer, index=False, sheet_name='MergedData')
                else:
                    df.to_excel(writer, index=False, sheet_name=sheet_name)

            writer.close()
            print(f"✅ Merged file created at: {output_path}")

        except Exception as e:
            print(f"❌ Error during merging files: {e}")

    def merge_files(self, output_filename):
        """Merge all Excel files in the folder into a single file"""
        try:
            # Get all Excel files in the folder
            excel_files = [f for f in os.listdir(self.folder_path) 
                          if f.endswith('.xlsx') and f != output_filename]
            
            if not excel_files:
                print("⚠️ No Excel files found to merge.")
                return
            
            # Create full paths
            file_paths = [os.path.join(self.folder_path, f) for f in excel_files]
            output_path = os.path.join(self.folder_path, output_filename)
            
            print(f"📁 Found {len(excel_files)} files to merge:")
            for f in excel_files:
                print(f"   - {f}")
            
            # Use the static merge method
            self.merge_specific_files(file_paths, output_path, one_sheet=False)
            
        except Exception as e:
            print(f"❌ Error during merge_files: {e}")

    def cleanup_files(self, exclude_files=None):
        exclude_files = exclude_files or []
        for f in os.listdir(self.folder_path):
            if f.endswith(".xlsx") and f not in exclude_files:
                try:
                    os.remove(os.path.join(self.folder_path, f))
                    print(f"🗑️ Deleted: {f}")
                except Exception as e:
                    print(f"⚠️ Could not delete {f}: {e}")
