"""
Python Compiler IDE - Flask Application
========================================
Entry point for the Flask web application.
Provides REST API endpoints for each compiler phase.
"""

import sys
import os

# Make sure internal modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, jsonify
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.semantic import SemanticAnalyzer
from symbol_table.symbol_table import SymbolTable

app = Flask(__name__)
app.config['SECRET_KEY'] = 'compiler-lab-air-university'


# -----------------------------------------------------------
# Shared compiler pipeline state per request
# -----------------------------------------------------------

def run_lexer(source_code):
    lexer = Lexer()
    tokens, errors = lexer.tokenize(source_code)
    token_dicts = [t.to_dict() for t in tokens]
    return token_dicts, lexer.get_results()


# -----------------------------------------------------------
# Routes
# -----------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lexer-page')
def lexer_page():
    return render_template('lexer.html')


@app.route('/parser-page')
def parser_page():
    return render_template('parser.html')


@app.route('/semantic-page')
def semantic_page():
    return render_template('semantic.html')


@app.route('/symbol-page')
def symbol_page():
    return render_template('symbol_table.html')


@app.route('/api/lexer', methods=['POST'])
def api_lexer():
    """
    POST /api/lexer
    Body: { "code": "<source code>" }
    Returns lexer tokens and errors.
    """
    data = request.get_json()
    source_code = data.get('code', '')

    if not source_code.strip():
        return jsonify({'error': 'No source code provided.'}), 400

    _, results = run_lexer(source_code)
    return jsonify(results)


@app.route('/api/parser', methods=['POST'])
def api_parser():
    """
    POST /api/parser
    Body: { "code": "<source code>" }
    Returns parsing result and steps.
    """
    data = request.get_json()
    source_code = data.get('code', '')

    if not source_code.strip():
        return jsonify({'error': 'No source code provided.'}), 400

    # Always run lexer first, then parser
    token_dicts, _ = run_lexer(source_code)

    parser = Parser()
    parser.parse(token_dicts)
    return jsonify(parser.get_results())


@app.route('/api/semantic', methods=['POST'])
def api_semantic():
    """
    POST /api/semantic
    Body: { "code": "<source code>" }
    Returns semantic analysis results.
    """
    data = request.get_json()
    source_code = data.get('code', '')

    if not source_code.strip():
        return jsonify({'error': 'No source code provided.'}), 400

    token_dicts, _ = run_lexer(source_code)

    analyzer = SemanticAnalyzer()
    analyzer.analyze(token_dicts)
    return jsonify(analyzer.get_results())


@app.route('/api/symbol_table', methods=['POST'])
def api_symbol_table():
    """
    POST /api/symbol_table
    Body: { "code": "<source code>" }
    Returns symbol table entries.
    """
    data = request.get_json()
    source_code = data.get('code', '')

    if not source_code.strip():
        return jsonify({'error': 'No source code provided.'}), 400

    token_dicts, _ = run_lexer(source_code)

    sym_table = SymbolTable()
    sym_table.build_from_tokens(token_dicts)
    return jsonify(sym_table.get_results())


@app.route('/api/analyze_all', methods=['POST'])
def api_analyze_all():
    """
    POST /api/analyze_all
    Body: { "code": "<source code>" }
    Runs all phases at once and returns combined results.
    """
    data = request.get_json()
    source_code = data.get('code', '')

    if not source_code.strip():
        return jsonify({'error': 'No source code provided.'}), 400

    # Phase 1: Lexer
    token_dicts, lex_results = run_lexer(source_code)

    # Phase 2: Parser
    parser = Parser()
    parser.parse(token_dicts)
    parse_results = parser.get_results()

    # Phase 3: Semantic
    analyzer = SemanticAnalyzer()
    analyzer.analyze(token_dicts)
    sem_results = analyzer.get_results()

    # Phase 4: Symbol Table
    sym_table = SymbolTable()
    sym_table.build_from_tokens(token_dicts)
    sym_results = sym_table.get_results()

    return jsonify({
        'lexer': lex_results,
        'parser': parse_results,
        'semantic': sem_results,
        'symbol_table': sym_results
    })


if __name__ == '__main__':
    print("=" * 45)
    print("  Python Compiler IDE")
    print("  http://127.0.0.1:5000")
    print("=" * 45)
    app.run(debug=True, port=5000)
