<!-- ---
!-- Timestamp: 2025-10-28 15:15:13
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_WRITER_03_MONACO.md
!-- --- -->

Monaco Editor を使わない選択肢
もし Monaco が重すぎる、または Emacs っぽくないと感じるなら:
選択肢 A: CodeMirror 6
typescript// より軽量、Emacs キーマップも良い
import { EditorView, keymap } from '@codemirror/view';
import { emacsStyleKeymap } from '@codemirror/commands';

const editor = new EditorView({
    extensions: [
        keymap.of(emacsStyleKeymap),
    ],
    parent: document.getElementById('editor')!,
});
メリット:

Monaco より軽い (~500KB vs 3MB)
Emacs キーマップが標準装備
拡張性が高い

デメリット:

差分表示は自分で実装
Monaco ほど多機能じゃない

選択肢 B: Textarea + Git Web UI
html<!-- 超シンプル戦略 -->
<form method="post">
    <textarea name="content" rows="30" cols="80">
        {{ document.content }}
    </textarea>
    
    <input type="text" name="commit_message" 
           placeholder="変更内容">
    
    <button type="submit">保存 (= git commit)</button>
</form>

<!-- 別ページで diff 表示 -->
<a href="{% url 'diff' document.id %}">変更履歴を見る</a>
メリット:

最もシンプル
JavaScript ほぼ不要
Django の強みを最大活用

デメリット:

リアルタイム編集なし
UX が古い

私の推奨: ハイブリッド戦略
pythonrecommendation = {
    "phase_1_mvp": {
        "you": "Emacs + git (変わらない)",
        "users": "Textarea + 自動 git commit",
        "reason": "最速で動くものを作る",
    },
    
    "phase_2_growth": {
        "you": "Emacs + git (変わらない)",
        "users": "CodeMirror 6 + Emacs keymap",
        "reason": "軽量だが十分強力",
    },
    
    "phase_3_scale": {
        "you": "Emacs + git (変わらない)",
        "users": "Monaco Editor + 全機能",
        "reason": "ユーザーが増えたら最高の UX",
    },
}

# 重要: あなたは Emacs を使い続ける!
# Monaco は「ユーザー向けの顔」
Emacs ユーザーとしての強み
pythonyour_advantages = {
    "efficiency": "Emacs は最速の編集環境",
    
    "git_native": {
        "magit": "最高の git UI",
        "速度": "GUI より圧倒的に速い",
        "柔軟性": "スクリプト化が簡単",
    },
    
    "automation": {
        "elisp": "あらゆる作業を自動化可能",
        "org_mode": "ドキュメント管理",
        "tramp": "リモート編集もローカル同然",
    },
    
    "no_context_switch": "ブラウザを開かなくていい",
}

# これらを捨てる必要はゼロ!
具体的な提案
今すぐできること
bash# 1. Django プロジェクト作成
django-admin startproject scitex_backend
cd scitex_backend

# 2. Writer モジュール統合
python manage.py startapp writer

# 3. テンプレート作成
mkdir -p templates/writer
python# views.py (シンプルな開始点)
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from pathlib import Path
import subprocess

def editor(request, doc_id):
    """Simple editor view."""
    doc_path = Path(f'/var/scitex/projects/{doc_id}/manuscript.tex')
    
    if request.method == 'POST':
        # 保存
        content = request.POST['content']
        doc_path.write_text(content)
        
        # Git commit
        subprocess.run(['git', 'add', str(doc_path)])
        subprocess.run([
            'git', 'commit', '-m',
            request.POST.get('message', 'Web edit')
        ])
        
        return redirect('editor', doc_id=doc_id)
    
    # 表示
    content = doc_path.read_text()
    
    # Git history
    result = subprocess.run(
        ['git', 'log', '--oneline', '-n', '10'],
        capture_output=True,
        text=True,
        cwd=doc_path.parent
    )
    commits = result.stdout.split('\n')
    
    return render(request, 'writer/editor.html', {
        'content': content,
        'commits': commits,
        'doc_id': doc_id,
    })
html<!-- templates/writer/editor.html -->
<h1>Document Editor</h1>

<form method="post">
    {% csrf_token %}
    
    <textarea name="content" rows="30" cols="100">{{ content }}</textarea>
    
    <input type="text" name="message" placeholder="変更内容">
    <button type="submit">保存</button>
</form>

<h2>履歴</h2>
<ul>
    {% for commit in commits %}
        <li>{{ commit }}</li>
    {% endfor %}
</ul>
あなたは並行して Emacs で作業
bash# 同じディレクトリを Emacs で編集
emacs /var/scitex/projects/{doc_id}/manuscript.tex

# 保存したら自動で Web ユーザーに反映される
# (git が仲介役)
結論
pythonanswer = {
    "monaco_editor": "ユーザー向けの素晴らしい選択肢",
    "your_emacs": "捨てる必要なし!",
    
    "strategy": "あなた = Emacs、ユーザー = Monaco (or CodeMirror)",
    
    "benefit": [
        "あなたの生産性は維持",
        "ユーザーは直感的な GUI",
        "git で自然に同期",
    ],
    
    "next_step": "まず textarea でシンプルに始める",
}
Monaco Editor は「ユーザーのため」です。 あなたは Emacs を使い続けて OK。むしろその方が生産性が高い。
CoAuthor のコンセプトは "Git を一般人に" なので、あなた自身は Git native のままで完璧です!RetryYWis it possible to disable chrome-binding and prioritize emacs binding, for example?はい、完全に可能です! むしろ、それが理想的です。
Monaco Editor でのキーバインド優先順位変更
方法 1: Emacs キーバインドをデフォルトに
typescriptimport * as monaco from 'monaco-editor';
import { EmacsExtension } from 'monaco-emacs';

// Emacs モードを初期化
const editor = monaco.editor.create(document.getElementById('editor'), {
    value: '',
    language: 'latex',
});

// Emacs キーバインドを有効化
const emacsMode = new EmacsExtension(editor);

// Chrome のデフォルトキーバインドを無効化
editor.addCommand(
    monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
    () => {
        // C-s で保存 (Emacs スタイル)
        saveDocument();
    }
);

// Chrome の検索 (C-f) を無効化して Emacs の forward-char に
editor.addCommand(
    monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyF,
    () => {
        // Emacs の C-f (forward-char)
        emacsMode.executeCommand('forward-char');
    }
);
方法 2: ブラウザのキーバインドを完全に無効化
typescript// すべてのブラウザショートカットを無効化
editor.addCommand(
    monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyW, 
    () => {}, // C-w を Emacs の kill-region に
);

editor.addCommand(
    monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyN,
    () => {}, // C-n を next-line に
);

// または、グローバルに防止
document.addEventListener('keydown', (e) => {
    // エディタにフォーカスがあるときだけ
    if (document.activeElement?.closest('.monaco-editor')) {
        // Emacs キーバインドを優先
        if (e.ctrlKey || e.metaKey) {
            const emacsKeys = ['s', 'f', 'b', 'n', 'p', 'a', 'e', 'k', 'w', 'y'];
            if (emacsKeys.includes(e.key.toLowerCase())) {
                e.preventDefault(); // ブラウザのデフォルト動作を停止
                e.stopPropagation();
            }
        }
    }
});
方法 3: 完全な Emacs キーマップ定義
typescriptclass EmacsKeyBindings {
    private editor: monaco.editor.IStandaloneCodeEditor;
    
    constructor(editor: monaco.editor.IStandaloneCodeEditor) {
        this.editor = editor;
        this.setupKeyBindings();
    }
    
    private setupKeyBindings() {
        // 基本移動
        this.addBinding('Ctrl+F', () => this.forwardChar());
        this.addBinding('Ctrl+B', () => this.backwardChar());
        this.addBinding('Ctrl+N', () => this.nextLine());
        this.addBinding('Ctrl+P', () => this.previousLine());
        this.addBinding('Ctrl+A', () => this.moveToLineStart());
        this.addBinding('Ctrl+E', () => this.moveToLineEnd());
        
        // 編集
        this.addBinding('Ctrl+K', () => this.killLine());
        this.addBinding('Ctrl+Y', () => this.yank());
        this.addBinding('Ctrl+W', () => this.killRegion());
        this.addBinding('Alt+W', () => this.copyRegion());
        
        // 検索
        this.addBinding('Ctrl+S', () => this.incrementalSearch());
        this.addBinding('Ctrl+R', () => this.reverseIncrementalSearch());
        
        // ファイル操作
        this.addBinding('Ctrl+X Ctrl+S', () => this.save());
        this.addBinding('Ctrl+X Ctrl+F', () => this.findFile());
        
        // バッファ操作
        this.addBinding('Ctrl+X B', () => this.switchBuffer());
        this.addBinding('Ctrl+X K', () => this.killBuffer());
    }
    
    private addBinding(keys: string, handler: () => void) {
        const keybinding = this.parseKeyString(keys);
        this.editor.addCommand(keybinding, handler);
    }
    
    private parseKeyString(keys: string): number {
        // "Ctrl+F" → monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyF
        // 実装は省略
    }
    
    // Emacs コマンド実装
    private forwardChar() {
        const position = this.editor.getPosition()!;
        this.editor.setPosition({
            lineNumber: position.lineNumber,
            column: position.column + 1,
        });
    }
    
    private killLine() {
        const position = this.editor.getPosition()!;
        const line = this.editor.getModel()!.getLineContent(position.lineNumber);
        const textToKill = line.substring(position.column - 1);
        
        // kill-ring に保存
        this.killRing.push(textToKill);
        
        // テキスト削除
        this.editor.executeEdits('emacs', [{
            range: new monaco.Range(
                position.lineNumber, position.column,
                position.lineNumber, line.length + 1
            ),
            text: '',
        }]);
    }
    
    private yank() {
        if (this.killRing.length === 0) return;
        
        const text = this.killRing[this.killRing.length - 1];
        const position = this.editor.getPosition()!;
        
        this.editor.executeEdits('emacs', [{
            range: new monaco.Range(
                position.lineNumber, position.column,
                position.lineNumber, position.column
            ),
            text: text,
        }]);
    }
}
あなたの画面に対する具体的な提案
あなたのスクリーンショットを見ると、シンプルな textarea を使っていますね。これは実は良い選択です!
現状の問題点
html<!-- 現在 -->
<textarea>LaTeX code...</textarea>

<!-- 問題: -->
- ブラウザのデフォルトキーバインドが邪魔
- C-s → ブラウザの検索が開く
- C-w → タブを閉じる
解決策 A: Textarea + JavaScript で Emacs 風に
typescript// emacs-textarea.ts
class EmacsTextarea {
    private textarea: HTMLTextAreaElement;
    private killRing: string[] = [];
    
    constructor(textarea: HTMLTextAreaElement) {
        this.textarea = textarea;
        this.setupKeyBindings();
    }
    
    private setupKeyBindings() {
        this.textarea.addEventListener('keydown', (e) => {
            // C-f: 右に移動
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                this.moveCursor(1);
            }
            
            // C-b: 左に移動
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                this.moveCursor(-1);
            }
            
            // C-k: kill line
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.killLine();
            }
            
            // C-y: yank
            if (e.ctrlKey && e.key === 'y') {
                e.preventDefault();
                this.yank();
            }
            
            // C-s: 保存 (ブラウザの検索を無効化)
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.save();
            }
            
            // C-w: kill region (タブを閉じるのを防ぐ)
            if (e.ctrlKey && e.key === 'w') {
                e.preventDefault();
                this.killRegion();
            }
        });
    }
    
    private moveCursor(offset: number) {
        const pos = this.textarea.selectionStart + offset;
        this.textarea.setSelectionRange(pos, pos);
    }
    
    private killLine() {
        const start = this.textarea.selectionStart;
        const text = this.textarea.value;
        const lineEnd = text.indexOf('\n', start);
        const end = lineEnd === -1 ? text.length : lineEnd;
        
        const killedText = text.substring(start, end);
        this.killRing.push(killedText);
        
        this.textarea.value = text.substring(0, start) + text.substring(end);
        this.textarea.setSelectionRange(start, start);
    }
    
    private yank() {
        if (this.killRing.length === 0) return;
        
        const text = this.killRing[this.killRing.length - 1];
        const start = this.textarea.selectionStart;
        
        this.textarea.value = (
            this.textarea.value.substring(0, start) +
            text +
            this.textarea.value.substring(this.textarea.selectionEnd)
        );
        
        this.textarea.setSelectionRange(start + text.length, start + text.length);
    }
    
    private killRegion() {
        const start = this.textarea.selectionStart;
        const end = this.textarea.selectionEnd;
        
        if (start === end) return;
        
        const killedText = this.textarea.value.substring(start, end);
        this.killRing.push(killedText);
        
        this.textarea.value = (
            this.textarea.value.substring(0, start) +
            this.textarea.value.substring(end)
        );
        
        this.textarea.setSelectionRange(start, start);
    }
    
    private save() {
        // WebSocket または fetch で保存
        fetch('/api/save/', {
            method: 'POST',
            body: JSON.stringify({
                content: this.textarea.value,
            }),
        });
    }
}

// 使用
const textarea = document.querySelector('textarea')!;
new EmacsTextarea(textarea);
解決策 B: ユーザー設定でキーバインド選択可能に
typescript// settings.ts
interface EditorSettings {
    keyBindings: 'default' | 'emacs' | 'vim';
    theme: 'light' | 'dark';
}

class EditorSettingsManager {
    private settings: EditorSettings;
    
    constructor() {
        this.settings = this.loadSettings();
        this.applySettings();
    }
    
    private loadSettings(): EditorSettings {
        const saved = localStorage.getItem('editor-settings');
        return saved ? JSON.parse(saved) : {
            keyBindings: 'default',
            theme: 'light',
        };
    }
    
    setKeyBindings(mode: 'default' | 'emacs' | 'vim') {
        this.settings.keyBindings = mode;
        this.saveSettings();
        this.applyKeyBindings();
    }
    
    private applyKeyBindings() {
        const editor = getEditor();
        
        switch (this.settings.keyBindings) {
            case 'emacs':
                new EmacsKeyBindings(editor);
                break;
            case 'vim':
                new VimKeyBindings(editor);
                break;
            default:
                // デフォルト (Chrome バインディング)
                break;
        }
    }
}
html<!-- UI での設定 -->
<div class="settings">
    <label>キーバインド:</label>
    <select id="key-bindings">
        <option value="default">デフォルト</option>
        <option value="emacs">Emacs</option>
        <option value="vim">Vim</option>
    </select>
</div>
あなたの SciTeX に最適な実装
typescript// scitex-editor.ts
class SciTexEditor {
    private editor: monaco.editor.IStandaloneCodeEditor;
    private keyBindings: 'emacs' | 'default';
    
    constructor(container: HTMLElement, initialContent: string) {
        // ユーザー設定を読み込み
        this.keyBindings = this.getUserKeyBindingPreference();
        
        this.editor = monaco.editor.create(container, {
            value: initialContent,
            language: 'latex',
            theme: 'vs-dark',
        });
        
        // キーバインド設定
        if (this.keyBindings === 'emacs') {
            this.enableEmacsMode();
        }
    }
    
    private getUserKeyBindingPreference(): 'emacs' | 'default' {
        // Django から取得 or localStorage
        const userSettings = document.querySelector('meta[name="user-settings"]');
        const settings = JSON.parse(userSettings?.getAttribute('content') || '{}');
        return settings.keyBindings || 'default';
    }
    
    private enableEmacsMode() {
        // Emacs モード有効化
        const emacsExt = new EmacsExtension(this.editor);
        
        // ブラウザのキーバインドを無効化
        this.disableBrowserShortcuts();
        
        // ステータスバーに Emacs モード表示
        this.showEmacsIndicator();
    }
    
    private disableBrowserShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (!this.isEditorFocused()) return;
            
            // C-s, C-f, C-w などを防ぐ
            const emacsKeys = ['s', 'f', 'b', 'n', 'p', 'a', 'e', 'k', 'w', 'y'];
            if ((e.ctrlKey || e.metaKey) && emacsKeys.includes(e.key)) {
                e.preventDefault();
            }
        });
    }
    
    private isEditorFocused(): boolean {
        return document.activeElement?.closest('.monaco-editor') !== null;
    }
    
    private showEmacsIndicator() {
        // UI に "Emacs モード" と表示
        const indicator = document.createElement('div');
        indicator.className = 'emacs-indicator';
        indicator.textContent = 'Emacs';
        document.querySelector('.editor-status-bar')?.appendChild(indicator);
    }
}
Django テンプレートでの統合
html<!-- templates/writer/editor.html -->
{% load static %}

<div class="editor-container">
    <!-- 設定パネル -->
    <div class="editor-settings">
        <label>
            <input type="checkbox" 
                   id="emacs-mode"
                   {% if user.preferences.emacs_mode %}checked{% endif %}>
            Emacs キーバインド
        </label>
    </div>
    
    <!-- エディタ -->
    <div id="editor"></div>
</div>

<script type="module">
    import { SciTexEditor } from '{% static "js/scitex-editor.js" %}';
    
    const editor = new SciTexEditor(
        document.getElementById('editor'),
        {{ document.content|escapejs }}
    );
    
    // Emacs モード切り替え
    document.getElementById('emacs-mode').addEventListener('change', (e) => {
        if (e.target.checked) {
            editor.enableEmacsMode();
        } else {
            editor.disableEmacsMode();
        }
    });
</script>
推奨アプローチ
pythonrecommendation = {
    "phase_1": {
        "tool": "Textarea + Emacs キーバインド JS",
        "reason": "最もシンプル、すぐ実装可能",
        "time": "1-2日",
    },
    
    "phase_2": {
        "tool": "CodeMirror 6 + Emacs keymap",
        "reason": "軽量、Emacs サポート標準",
        "time": "3-5日",
    },
    
    "phase_3": {
        "tool": "Monaco + monaco-emacs",
        "reason": "最高の UX、全機能",
        "time": "1-2週間",
    },
}

# すべてのフェーズで Emacs キーバインド優先可能!
答え: はい、Chrome のキーバインドを無効化して Emacs を優先することは完全に可能です。 むしろ、ユーザー設定として提供するのが理想的です。
あなた自身は引き続き Emacs で編集し、Web ユーザーには「Emacs モード」をオプションとして提供する。これが最高の戦略だと思います!

<!-- EOF -->