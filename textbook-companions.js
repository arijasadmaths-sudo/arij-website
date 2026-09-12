/* Chapter deep links open their target without hiding the static catalogue. */
(() => {
  function openChapter() {
    let id;
    try { id = decodeURIComponent(window.location.hash.slice(1)); } catch (_) { return; }
    const target = document.getElementById(id);
    if (target && target.matches('details.chapter')) target.open = true;
  }
  window.addEventListener('hashchange', openChapter);
  openChapter();
})();
