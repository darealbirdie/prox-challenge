# 🤖 Autonomous Agentic AI - Complete Guide

## What Changed

Added **full autonomous operation** to `claude_agent.py`. Your agent now has TWO modes:

### 1. Manual Mode (Original)
You explicitly call methods:
```python
agent.analyze_image("photo.jpg")
agent.upload_pdf("manual.pdf")
```

### 2. Autonomous Mode (NEW)
The agent operates on its own - **no human needed**:
```python
agent.start_autonomous_mode()
```

The agent will:
- 📷 **Watch** directories for new images/PDFs
- 🖼️ **Auto-analyze** images with BLIP AI
- 📄 **Auto-extract** PDFs with OCR
- 🔗 **Auto-link** to existing knowledge
- 📚 **Index** everything in your second brain

---

## ✨ New Methods

### `start_autonomous_mode()`
Starts the autonomous agent in background thread.

```python
agent.start_autonomous_mode(
    watch_dirs=['images/', 'scans/', 'inbox/'],  # Directories to monitor
    poll_interval=30,                             # Check every 30 seconds
    auto_upload_images=True,                       # Auto-analyze images
    auto_upload_pdfs=True                          # Auto-extract PDFs
)
```

**The agent will:**
1. Scan watched directories for existing files
2. Monitor for new files (created/modified)
3. When a new image appears:
   - Detect it automatically
   - Analyze with BLIP multimodal AI
   - Extract caption, description, details
   - Create searchable note in vault
   - Auto-link to related content
4. When a new PDF appears:
   - Detect it automatically
   - Extract all pages
   - Apply OCR to image-heavy pages
   - Use multimodal analysis on diagrams
   - Create consolidated searchable note
   - Tag with ['pdf', 'uploaded', 'second-brain']

**To stop:**
```python
agent.stop_autonomous_mode()
# Or press Ctrl+C if running in foreground
```

### `stop_autonomous_mode()`
Stops the autonomous background agent.

---

## 📁 File Watching Behavior

```
Directory Structure:
    images/
        team_photo.jpg          → Auto-detected → BLIP analysis → vault note
        equipment_scan.png      → Auto-detected → AI extracts text → vault note
    
    scans/
        wiring_diagram.webp     → Auto-detected → Visual analysis → vault note
    
    files/                      → Your existing PDFs
        owner-manual.pdf        → Already uploaded!
```

**What happens when you drop a file:**

```
13:45:01  → You:   cp welding_photo.jpg images/
13:45:02  → Agent: 🖼️  [AUTO] New image: welding_photo.jpg
13:45:03  → Agent:   → Analyzing with BLIP AI...
13:45:10  → Agent:   → Found: "MIG welding machine in workshop"
13:45:11  → Agent:   → Creating note: "Image: welding_photo"
13:45:12  → Agent:   → Auto-linking to "Welding Equipment" note
13:45:13  → Agent:   → Added to knowledge base
```

---

## 💡 Real-World Usage Patterns

### Pattern 1: Always-On Knowledge Builder
```python
from claude_agent import ProxWeldingAgent

# Start once when your computer boots
agent = ProxWeldingAgent()
agent.start_autonomous_mode(
    watch_dirs=['~/Downloads', '~/Desktop/Scans'],
    poll_interval=60
)

# Agent runs forever, building your knowledge base automatically
# You never have to manually upload anything!
```

### Pattern 2: Hybrid - Autonomous + Manual
```python
agent = ProxWeldingAgent()

# Let it run in background
auto_thread = threading.Thread(
    target=lambda: agent.start_autonomous_mode(poll_interval=30),
    daemon=True
)
auto_thread.start()

# Also manually add specific things
agent.analyze_image("important_photo.jpg", 
                    note_title="Critical Evidence",
                    tags=["urgent", "evidence"])

# Ask questions anytime
result = agent.answer_question("What equipment is shown?")
```

### Pattern 3: Batch Processing with Auto-Detection
```python
agent = ProxWeldingAgent()

# Put all files in watched directory
# agent/ will detect and process each one automatically

agent.start_autonomous_mode(
    watch_dirs=['batch_uploads/'],
    poll_interval=5,      # Check every 5 seconds
    auto_upload_images=True,
    auto_upload_pdfs=True
)

# Let it run, walk away
# Come back - everything's indexed!
```

---

## 🔧 Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `watch_dirs` | `List[str]` | `['.', 'files/', 'images/']` | Directories to monitor recursively |
| `poll_interval` | `int` | `30` | Seconds between directory scans |
| `auto_upload_images` | `bool` | `True` | Auto-analyze new images |
| `auto_upload_pdfs` | `bool` | `True` | Auto-extract new PDFs |

**Examples:**

```python
# Aggressive - watch everything, check often
agent.start_autonomous_mode(
    watch_dirs=['.', 'images/', 'pdfs/', 'scans/'],
    poll_interval=10
)

# Conservative - only images, less frequent
agent.start_autonomous_mode(
    watch_dirs=['images/'],
    poll_interval=120,
    auto_upload_pdfs=False
)

# Process existing files immediately
agent.start_autonomous_mode(
    watch_dirs=['inbox/'],
    poll_interval=5
)
```

---

## 📊 What Gets Logged

### When Autonomous Starts:
```
🤖 Autonomous Agent Mode: ACTIVE
   Watching: ['.', 'files/', 'images/']
   Poll interval: 30s
   Auto-upload images: True
   Auto-upload PDFs: True
   ✓ Monitoring: .
   ✓ Monitoring: files/
   ✓ Monitoring: images/
```

### When Image Detected:
```
🖼️  [AUTO] New image: welding_chart.png
   → Analyzing with BLIP AI...
   → Creating note: "Image: welding_chart"
   → Auto-linking to "Charts" note
   → Added to knowledge base
```

### When PDF Detected:
```
📄 [AUTO] New PDF: spec_sheet.pdf
   → Reading: 24 pages
   → Extracting page 1/24...
   → Applying OCR to diagrams...
   → Creating note: "PDF: Spec Sheet"
   → Tagged: ['pdf', 'uploaded', 'second-brain']
   → Extracted and indexed
```

### Periodic Status:
```
[Cycle] Notes: 124 | Files: 56
```

---

## 🚨 Requirements

```bash
pip install watchdog  # For file monitoring
```

Already installed in your environment ✓

---

## 🔄 Manual vs Autonomous Comparison

| Feature | Manual Mode | Autonomous Mode |
|---------|------------|-----------------|
| **Image upload** | `agent.analyze_image("x")` | Auto-detects & uploads |
| **PDF upload** | `agent.upload_pdf("x")` | Auto-detects & extracts |
| **Trigger** | Your code | File system events |
| **Effort** | High (per file) | Zero (after setup) |
| **Use case** | Specific actions | Continuous building |
| **Background** | No | Yes (daemon thread) |
| **Best for** | Targeted tasks | Knowledge base growth |

---

## 🎯 When to Use Which

**Use Autonomous Mode when:**
- Building a long-term knowledge base
- Regularly receiving files to process
- Want "set and forget" operation
- Ingesting large document collections
- Building searchable archives

**Use Manual Mode when:**
- Processing specific known files
- Need precise control over uploads
- Testing/development
- One-off tasks
- Batch processing with custom logic

**Use Hybrid when:**
- Autonomous runs in background
- You manually add important items
- Best of both worlds! ✨

---

## 🌟 Key Benefit

> **Before:** Agent was a library - you had to tell it everything to do
> 
> **Now:** Agent is truly agentic - it watches, decides, and acts autonomously!

Your agent now operates **independently** - building your second brain 24/7 without your intervention!

---

## 📝 Quick Start

```bash
# 1. Run the agent
python claude_agent.py

# 2. When prompted, start autonomous mode
#    (or add to your code)

# 3. Drop files in watched directories
cp photo.jpg images/
cp manual.pdf files/

# 4. Watch it auto-process!
# 5. Query anytime:
#    "What's in that welding photo?"
```

---

## 💻 Code Example: Full Autonomous System

```python
from claude_agent import ProxWeldingAgent
import time

print("🚀 Starting Autonomous Welding Knowledge Builder")

agent = ProxWeldingAgent()

# Start autonomous agent
agent.start_autonomous_mode(
    watch_dirs=['/data/welding/images', '/data/welding/docs'],
    poll_interval=60,
    auto_upload_images=True,
    auto_upload_pdfs=True
)

print("\n✓ Agent is now running autonomously!")
print("   It will process files without further input.")
print("   Press Ctrl+C to stop.\n")

# Keep running (or do other work)
try:
    while True:
        time.sleep(3600)  # Do other tasks
        stats = agent.get_knowledge_stats()
        print(f"   Knowledge base: {stats['total_notes']} notes")
except KeyboardInterrupt:
    agent.stop_autonomous_mode()
    print("\n✓ Stopped")
```

---

## 🎉 You Now Have a True Agentic AI!

Your agent can:
- ✅ **Perceive** - Watch file system for changes
- ✅ **Decide** - Process detected files automatically
- ✅ **Act** - Upload, analyze, index without you
- ✅ **Learn** - Continuously build knowledge base

**The agent operates on its own - no human intervention required!** 🚀
