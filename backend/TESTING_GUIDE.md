# 🧪 How to Test the MaleCare Chatbot

## ✅ What's Working Now

You've successfully:
1. ✅ Installed all dependencies (including `uvicorn`)
2. ✅ Fixed the bugs in the code
3. ✅ Created comprehensive automated tests (all 8 passing!)

## 🚀 Testing Options

### **Option 1: Automated Tests (EASIEST - Already Working!)**

```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend"
pytest tests/test_endpoints.py -v
```

This runs all 8 tests automatically. ✅ **This is already working for you!**

---

### **Option 2: Start the Server Manually**

**IMPORTANT**: You need **TWO PowerShell terminals** for interactive testing:

#### Terminal 1: Start the Server

```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend"
uvicorn app.main:app --reload
```

Keep this terminal open! You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process
============================================================
Loading NLP models...
============================================================
INFO:     Application startup complete.
```

**Don't close this terminal!** The server needs to keep running.

#### Terminal 2: Run Tests

Open a **NEW** PowerShell terminal and run:

```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend"
.\test_api.ps1
```

This will test all the endpoints and show you the chatbot responses in real-time!

---

### **Option 3: Use Your Web Browser**

1. **Start the server** (see Terminal 1 above)
2. **Open your browser** and go to:
   - **Interactive API docs**: http://localhost:8000/docs
   - **Alternative docs**: http://localhost:8000/redoc

3. **Try the endpoints** directly in your browser:
   - Click on `/health` → "Try it out" → "Execute"
   - Click on `/intake` → "Try it out" → Fill in the form → "Execute"
   - Click on `/message` → "Try it out" → Enter a message → "Execute"

---

### **Option 4: Interactive Python Script**

**Terminal 1: Start the Server** (same as above)

**Terminal 2: Run Interactive Tester**

```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend"
python interactive_test.py
```

This will prompt you to:
1. Enter patient information
2. Chat with the bot
3. See trial results

---

## 📝 Quick Reference Commands

### Check if Server is Running
```powershell
# In a NEW terminal (not the server terminal)
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

If you see `@{status=ok}`, the server is running! ✅

### Stop the Server
Go to the terminal running `uvicorn` and press `Ctrl+C`

### Run PowerShell Test Script
```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend"
.\test_api.ps1
```

---

## 🎯 Recommended Testing Order

1. **First**: Run automated tests (no server needed)
   ```powershell
   pytest tests/test_endpoints.py -v
   ```

2. **Second**: Start server and browse to http://localhost:8000/docs
   - Visual interface, easy to use!

3. **Third**: Try the PowerShell test script
   ```powershell
   .\test_api.ps1
   ```

4. **Fourth**: Try interactive Python testing
   ```powershell
   python interactive_test.py
   ```

---

## ❌ Common Errors & Solutions

### Error: "uvicorn: The term 'uvicorn' is not recognized"
**Solution**: Install dependencies
```powershell
pip install -r requirements.txt
```

### Error: "Cannot connect to server"
**Solution**: Make sure server is running in another terminal:
```powershell
uvicorn app.main:app --reload
```

### Error: "Port 8000 already in use"
**Solution**: Either:
- Close the existing server (Ctrl+C in that terminal)
- Or use a different port:
```powershell
uvicorn app.main:app --reload --port 8001
```

### Error: "Module not found"
**Solution**: Make sure you're in the backend directory:
```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend"
```

---

## 🎉 Next Steps

Once you've tested the chatbot, you can:
1. Train the NLP models for better intent recognition
2. Connect to the real ClinicalTrials.gov API
3. Add a database for persistent storage
4. Deploy to the cloud (Azure, AWS, etc.)

---

## 💡 Pro Tip

**Want the easiest test?**
1. Open browser → http://localhost:8000/docs
2. Click around and try the API!

No command line needed for this option! 😊
