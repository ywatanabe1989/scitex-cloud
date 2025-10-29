<!-- ---
!-- Timestamp: 2025-10-30 00:39:30
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/suggestions.md
!-- --- -->

- [ ] Slider should be prepared between the panels 
  - [ ] to change width (ratio) between them
- [ ] The scrollbar of the PDF view should be theme-responsible
- [ ] The top of PDF should not have margin
- [ ] Font sizes can be adjustable
- [ ] [checkbox] Auto Preview (5 s)
- [ ] Preview button

- [ ] Latex pane and preview pane have 50%:50% widths
  - [ ] Just place splitter between them

なるほど!2つの問題がありますね:

中央に謎の灰色のスペース (スライダーが変な位置に)
PDF上部に大きな余白 (MANUSCRIPT PDFヘッダーの下)

修正方法
問題1: 中央の灰色スペースを削除
これはスプリッター(リサイズ用のバー)が表示されているようです。
css/* 不要なスプリッターを非表示 */
.split-pane-divider {
    display: none !important;
}

/* または、スプリッター自体を削除 */
F12のConsoleで即座に試す:
javascript// スプリッターを探して削除
const divider = document.querySelector('.split-pane-divider');
if (divider) {
    divider.remove();
}

// または非表示に
const dividers = document.querySelectorAll('[style*="col-resize"]');
dividers.forEach(d => d.style.display = 'none');
問題2: PDF上部の余白を削除
css/* PDFビューアーヘッダーとコンテナの修正 */
.preview-header,
.pdf-header {
    padding: 8px 16px;
    height: 44px;
    margin: 0;
}

.pdf-viewer-container {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

.pdf-viewer-container iframe {
    margin: 0 !important;
    padding: 0 !important;
    display: block;
}
F12のConsoleで即座に試す:

<!-- EOF -->