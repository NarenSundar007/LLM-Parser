# 🚀 Groq Setup Guide for Free LLM Access

## 🎯 Why Groq?

✅ **FREE Tier**: Generous free tier with high-quality models
✅ **Fast Inference**: Lightning-fast response times
✅ **Great Models**: Llama 3.1 70B, Mixtral 8x7B, and more
✅ **Easy API**: Compatible with OpenAI-style API calls

## 🔑 Getting Your Groq API Key

### Step 1: Sign Up
1. Go to: https://console.groq.com/
2. Sign up with email or GitHub
3. Verify your email address

### Step 2: Get API Key
1. Go to API Keys section
2. Click "Create API Key"
3. Copy your API key (starts with `gsk_`)

### Step 3: Configure System
1. Copy `.env.example` to `.env`
2. Add your Groq API key:
```bash
GROQ_API_KEY=gsk_your_api_key_here
```

## 🤖 Best Free Groq Models

### 1. **llama-3.1-70b-versatile** (RECOMMENDED)
- **Best overall model** for complex reasoning
- **70B parameters** - excellent for document analysis
- **High accuracy** for query parsing and logic evaluation
- **Current default** in the system

### 2. **llama-3.1-8b-instant**
- **Fastest responses** (~100ms)
- **Good for simple queries**
- **Lower accuracy** than 70B version

### 3. **mixtral-8x7b-32768**
- **Large context window** (32K tokens)
- **Good for long documents**
- **Balanced speed/accuracy**

### 4. **gemma2-9b-it**
- **Google's Gemma model**
- **Good instruction following**
- **Efficient for structured tasks**

## 📊 Model Comparison

| Model | Speed | Accuracy | Context | Best For |
|-------|-------|----------|---------|----------|
| llama-3.1-70b-versatile | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 8K | Complex analysis |
| llama-3.1-8b-instant | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 8K | Quick responses |
| mixtral-8x7b-32768 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 32K | Long documents |
| gemma2-9b-it | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8K | Structured tasks |

## ⚙️ Configuration Options

### Default (Recommended)
```bash
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile
EMBEDDING_MODEL=sentence-transformers
```

### For Speed-Critical Applications
```bash
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=sentence-transformers
```

### For Long Documents
```bash
LLM_PROVIDER=groq
LLM_MODEL=mixtral-8x7b-32768
EMBEDDING_MODEL=sentence-transformers
```

## 🆓 Free Tier Limits

- **Requests per minute**: 30 for 70B models, 100 for smaller models
- **Requests per day**: 14,400 for 70B models
- **Tokens per minute**: 6,000 for 70B models
- **No credit card required**

## 🔄 Fallback Strategy

The system automatically handles API limits:

1. **Primary**: Groq Llama 3.1 70B
2. **Fallback 1**: Groq Llama 3.1 8B (faster)
3. **Fallback 2**: Local processing (basic parsing)

## 🧪 Testing Your Setup

```bash
# 1. Check configuration
python check_config.py

# 2. Test with examples
python examples/usage_examples.py

# 3. Start the system
python main.py
```

## 📈 Performance Comparison

### Groq vs OpenAI

| Aspect | Groq (Free) | OpenAI (Paid) |
|--------|-------------|---------------|
| **Cost** | 🟢 FREE | 🔴 $0.50-2.00/1M tokens |
| **Speed** | 🟢 Very Fast | 🟡 Moderate |
| **Quality** | 🟢 Excellent | 🟢 Excellent |
| **Models** | Llama, Mixtral | GPT-3.5/4 |
| **Rate Limits** | 🟡 Moderate | 🟢 High |

## 🛠️ Troubleshooting

### Common Issues

**❌ "Invalid API Key"**
- Check key format (should start with `gsk_`)
- Verify key is active in Groq console
- Check for typos in .env file

**❌ "Rate limit exceeded"**
- Wait 1 minute and retry
- Switch to faster model (8B instead of 70B)
- Implement request batching

**❌ "Model not found"**
- Check model name spelling
- Verify model is available in your region
- Use fallback model

### Debug Commands

```bash
# Test Groq connection
curl -H "Authorization: Bearer $GROQ_API_KEY" \
  https://api.groq.com/openai/v1/models

# Check system health
curl http://localhost:8000/health
```

## 🎉 Ready to Go!

With Groq, you get:
✅ **No API costs** for development
✅ **Fast responses** for better UX
✅ **State-of-the-art models** for accuracy
✅ **Easy integration** with existing code

Your LLM-powered query system is now **completely free** to run! 🚀

---

*💡 Pro Tip: Start with llama-3.1-70b-versatile for best results, then optimize for speed if needed.*
