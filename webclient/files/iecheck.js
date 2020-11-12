function showBrowserAlert() {
   if (ieVersion() < 12) {
        alert('Warning: Internet Explorer 11 and below are unsupported. Please use a recent version of Chrome or Firefox.')
   }
}

document.addEventListener('DOMContentLoaded', showBrowserAlert);

function ieVersion(uaString) {
    uaString = uaString || navigator.userAgent;
    var match = /\b(MSIE |Trident.*?rv:|Edge\/)(\d+)/.exec(uaString);
    if (match) return parseInt(match[2])
}

