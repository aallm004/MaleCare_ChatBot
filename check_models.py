"""
Script to check if your trained models exist and where they are
"""

import os
from pathlib import Path

def check_model_folder(folder_name):
    """Check if a model folder exists and what's inside"""
    
    print(f"\n{'='*60}")
    print(f"Checking for: {folder_name}")
    print(f"{'='*60}")
    
    # Check current directory
    if os.path.exists(folder_name):
        print(f"✅ FOUND in current directory: {os.path.abspath(folder_name)}")
        print(f"\n📂 Contents:")
        
        for item in os.listdir(folder_name):
            item_path = os.path.join(folder_name, item)
            size = os.path.getsize(item_path)
            size_mb = size / (1024 * 1024)
            print(f"  - {item} ({size_mb:.2f} MB)")
        
        # Check for required files
        required_files = ['pytorch_model.bin', 'config.json', 'label_map.json']
        missing = []
        for req_file in required_files:
            if not os.path.exists(os.path.join(folder_name, req_file)):
                missing.append(req_file)
        
        if missing:
            print(f"\n⚠️  WARNING: Missing required files: {', '.join(missing)}")
        else:
            print(f"\n✅ All required files present!")
        
        return True
    else:
        print(f"❌ NOT FOUND in current directory")
        print(f"   Looking elsewhere...")
        
        # Search in common locations
        search_paths = [
            Path.home(),  # Home directory
            Path.cwd().parent,  # Parent directory
            Path.cwd() / "models",  # models subfolder
        ]
        
        for search_path in search_paths:
            model_path = search_path / folder_name
            if model_path.exists():
                print(f"✅ FOUND at: {model_path}")
                return True
        
        print(f"❌ Could not find {folder_name} anywhere")
        print(f"\n💡 This means:")
        print(f"   1. Training may not have completed successfully")
        print(f"   2. Or it saved to a different location")
        print(f"   3. Or you need to run train_models.py first")
        
        return False

def main():
    print("\n" + "="*60)
    print("ML MODEL LOCATION CHECKER")
    print("="*60)
    print(f"Current directory: {os.getcwd()}")
    
    # Check both models
    intent_found = check_model_folder("intent_model")
    ner_found = check_model_folder("ner_model")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    if intent_found and ner_found:
        print("✅ Both models found and ready for deployment!")
    elif intent_found or ner_found:
        print("⚠️  Only one model found - you need to retrain the missing one")
    else:
        print("❌ No models found - you need to run training")
        print("\n📝 Next steps:")
        print("   1. Make sure you have intent_training_data.json")
        print("   2. Make sure you have ner_training_data.json")
        print("   3. Run: python train_models.py")
        print("   4. Wait for training to complete (10-20 minutes)")
        print("   5. Run this script again to verify")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()