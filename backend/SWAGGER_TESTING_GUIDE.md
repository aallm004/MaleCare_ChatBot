# 🧪 How to Test the API in Swagger UI (http://localhost:8000/docs)

## ✅ What Was Wrong

You were getting an **"Internal Server Error"** because:
1. The `/message` endpoint wasn't properly configured to accept JSON in Swagger UI
2. The request body was empty (JSON decode error)

**I fixed this!** The endpoint now uses proper Pydantic models, so Swagger UI will automatically show you the correct form to fill out.

---

## 📋 Step-by-Step Testing Guide

### **Step 1: Start the Server**

```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend"
uvicorn app.main:app --reload
```

Wait for this message:
```
INFO:     Application startup complete.
```

### **Step 2: Open Swagger UI**

Go to: **http://localhost:8000/docs**

You should see a page titled **"Cancer Trial Match Chatbot API"** with 4 endpoints.

---

## 🎯 Testing the Endpoints in Order

### **Test 1: Health Check** ✅

1. Click on **GET `/health`** (blue button)
2. Click **"Try it out"**
3. Click **"Execute"**
4. ✅ You should see:
   ```json
   {
     "status": "ok"
   }
   ```

---

### **Test 2: Submit Intake Form** ✅

1. Click on **POST `/intake`** (green button)
2. Click **"Try it out"**
3. You'll see a JSON editor with example data
4. **Fill in the form** (or use the defaults):
   ```json
   {
     "user_id": "testuser123",
     "cancer_type": "breast cancer",
     "stage": "stage 2",
     "age": 45,
     "sex": "female",
     "location": "California",
     "comorbidities": [
       "diabetes"
     ],
     "prior_treatments": [
       "chemotherapy"
     ]
   }
   ```
5. Click **"Execute"**
6. ✅ You should see a response like:
   ```json
   {
     "response": "Thank you for sharing that information with me. How can I help you find clinical trials today?",
     "intake_complete": true
   }
   ```

**Important:** Remember the `user_id` you used! You'll need it for the next steps.

---

### **Test 3: Send a Message** ✅

1. Click on **POST `/message`** (green button)
2. Click **"Try it out"**
3. **Fill in the JSON** with the SAME `user_id`:
   ```json
   {
     "user_id": "testuser123",
     "message": "Find me clinical trials in Los Angeles"
   }
   ```
4. Click **"Execute"**
5. ✅ You should see a response like:
   ```json
   {
     "response": "Here are some breast cancer clinical trials in California:",
     "trials": [
       {
         "nct_id": "NCT12345678",
         "title": "A Study for breast cancer in California",
         "phase": "Phase 2",
         "status": "Recruiting",
         "location": "California",
         "link": "https://clinicaltrials.gov/study/NCT12345678"
       }
     ]
   }
   ```

---

### **Test 4: End Session** ✅

1. Click on **POST `/end-session`** (green button)
2. Click **"Try it out"**
3. **Fill in the JSON** with the SAME `user_id`:
   ```json
   {
     "user_id": "testuser123"
   }
   ```
4. Click **"Execute"**
5. ✅ You should see:
   ```json
   {
     "status": "session_cleared"
   }
   ```

---

## 🔑 Key Points

### **MUST USE THE SAME `user_id` FOR ALL REQUESTS**

The chatbot tracks your conversation using the `user_id`. If you change it between requests, the bot won't remember your intake information.

### **Correct Testing Order:**

1. ✅ `/health` - Check server is running
2. ✅ `/intake` - Submit patient information FIRST
3. ✅ `/message` - Now you can send messages
4. ✅ `/end-session` - Clear your session when done

### **What Happens If You Skip `/intake`?**

If you try to send a message WITHOUT first submitting the intake form, you'll get:

```json
{
  "response": "Please complete the intake form before proceeding.",
  "requires_intake": true
}
```

This is correct behavior! The chatbot requires patient information before it can help.

---

## 💡 Pro Tips

### **Tip 1: Try Different Messages**

After submitting intake, try different types of messages:

**Greeting:**
```json
{
  "user_id": "testuser123",
  "message": "Hello!"
}
```

**Find Trials:**
```json
{
  "user_id": "testuser123",
  "message": "Can you find trials for me?"
}
```

**Goodbye:**
```json
{
  "user_id": "testuser123",
  "message": "Thanks, goodbye!"
}
```

### **Tip 2: Use Different User IDs for Multiple Tests**

Each `user_id` maintains a separate conversation:

- `user_id: "alice"` → Alice's conversation
- `user_id: "bob"` → Bob's conversation

They won't interfere with each other!

### **Tip 3: Check the Terminal**

Watch the terminal where uvicorn is running to see:
- Requests coming in
- NLP predictions
- Any errors

---

## ❌ Common Errors & Solutions

### Error: "Internal Server Error (500)"

**Cause:** Missing required fields in the JSON

**Solution:** Make sure ALL required fields are filled:
- `user_id` - Always required
- `message` - Required for `/message`
- For `/intake`: `cancer_type`, `stage`, `age`, `sex`, `location`

### Error: "Please complete the intake form"

**Cause:** Trying to send a message before submitting intake

**Solution:** Submit the `/intake` form first

### Error: Server not responding

**Cause:** Server isn't running

**Solution:** 
```powershell
cd backend
uvicorn app.main:app --reload
```

---

## 📸 What You Should See

### Successful `/intake` Response:
![image](https://via.placeholder.com/600x100/4CAF50/FFFFFF?text=✓+Intake+Complete)

### Successful `/message` Response with Trials:
![image](https://via.placeholder.com/600x100/2196F3/FFFFFF?text=✓+Trials+Found)

---

## 🎯 Quick Test Sequence

**Copy and paste these in order:**

1. **Health Check** (GET /health)
   - Just click "Try it out" → "Execute"

2. **Submit Intake** (POST /intake)
   ```json
   {
     "user_id": "demo123",
     "cancer_type": "prostate cancer",
     "stage": "stage 1",
     "age": 60,
     "sex": "male",
     "location": "New York"
   }
   ```

3. **Send Message** (POST /message)
   ```json
   {
     "user_id": "demo123",
     "message": "Find me clinical trials"
   }
   ```

4. **End Session** (POST /end-session)
   ```json
   {
     "user_id": "demo123"
   }
   ```

---

## ✅ You're Testing Correctly Now!

The error you saw was because the endpoint wasn't set up properly. I fixed it by:
- ✅ Adding proper Pydantic models (`MessageRequest`, `EndSessionRequest`)
- ✅ Removing the manual JSON parsing
- ✅ Making Swagger UI automatically show the correct form

**Now when you click "Try it out" on `/message`, you'll see a proper form with `user_id` and `message` fields!**

---

Happy Testing! 🎉
