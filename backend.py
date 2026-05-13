#!/usr/bin/env python3
"""
Flask Backend for React Frontend
Connects React UI to Claude Agent
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

from claude_agent import ProxWeldingAgent

app = Flask(__name__)
CORS(app)

# Initialize agent on startup
print("🚀 Initializing Prox Welding Agent...")
agent = ProxWeldingAgent()
stats = agent.get_knowledge_stats()
print(f"✓ Agent ready: {stats['total_notes']} notes")

@app.route('/api/health', methods=['GET', 'POST'])
def health():
    """Health check endpoint"""
    stats = agent.get_knowledge_stats()
    return jsonify({
        'status': 'ok',
        'message': 'Agent connected',
        'notes': stats['total_notes'],
        'tags': len(stats['tags'])
    })

@app.route('/api/ask', methods=['POST'])
def ask():
    """Main question endpoint"""
    data = request.json
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({
            'error': 'Question is required'
        }), 400
    
    try:
        print(f"❓ Question: {question}")
        result = agent.answer_question(question)
        
        print(f"✓ Response generated ({len(result.get('answer', ''))} chars)")
        
        return jsonify({
            'answer': result['answer'],
            'artifacts': result.get('artifacts', []),
            'sources': result.get('sources', []),
            'context_used': result.get('context_used', False)
        })
    except Exception as e:
        print(f"✗ Error: {e}")
        return jsonify({
            'error': str(e),
            'answer': f"I encountered an error: {e}"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get knowledge base stats"""
    stats = agent.get_knowledge_stats()
    return jsonify({
        'notes': stats['total_notes'],
        'tags': len(stats['tags']),
        'tags_detail': stats['tags']
    })

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze uploaded image"""
    data = request.json
    image_path = data.get('image_path')
    note_title = data.get('note_title')
    
    if not image_path:
        return jsonify({'error': 'image_path required'}), 400
    
    try:
        result = agent.analyze_image(image_path, note_title=note_title)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload and extract PDF"""
    data = request.json
    pdf_path = data.get('pdf_path')
    
    if not pdf_path:
        return jsonify({'error': 'pdf_path required'}), 400
    
    try:
        result = agent.upload_pdf(pdf_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/autonomous/start', methods=['POST'])
def start_autonomous():
    """Start autonomous mode"""
    data = request.json or {}
    
    try:
        agent.start_autonomous_mode(
            watch_dirs=data.get('watch_dirs', None),
            poll_interval=data.get('poll_interval', 30),
            auto_upload_images=data.get('auto_upload_images', True),
            auto_upload_pdfs=data.get('auto_upload_pdfs', True)
        )
        return jsonify({'status': 'started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/autonomous/stop', methods=['POST'])
def stop_autonomous():
    """Stop autonomous mode"""
    try:
        agent.stop_autonomous_mode()
        return jsonify({'status': 'stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Backend Server Starting")
    print("="*60)
    print("📍 URL: http://localhost:5001")
    print("📝 API Endpoints:")
    print("   POST /api/health     - Health check")
    print("   POST /api/ask       - Ask a question")
    print("   GET  /api/stats     - Knowledge base stats")
    print("   POST /api/analyze-image - Analyze image")
    print("   POST /api/upload-pdf    - Upload PDF")
    print("   POST /api/autonomous/start - Start autonomous mode")
    print("   POST /api/autonomous/stop  - Stop autonomous mode")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
