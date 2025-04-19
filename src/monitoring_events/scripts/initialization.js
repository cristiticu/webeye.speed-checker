(() => {
    window.__pwMetrics = {};

    new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
            if (entry) {
                window.__pwMetrics['redirect-duration'] = Math.round(entry.redirectEnd - entry.redirectStart);
                window.__pwMetrics['dns-duration'] = Math.round(entry.domainLookupEnd - entry.domainLookupStart);
                window.__pwMetrics['tcp-handshake-duration'] = Math.round(entry.connectEnd - entry.connectStart);
                window.__pwMetrics['tls-duration'] = Math.round(entry.secureConnectionStart > 0 ? entry.connectEnd - entry.secureConnectionStart : 0);
                window.__pwMetrics['backend-duration'] = Math.round(entry.responseStart - entry.requestStart);
                window.__pwMetrics['time-to-first-byte'] = Math.round(entry.responseStart);
                window.__pwMetrics['download-duration'] = Math.round(entry.responseEnd - entry.responseStart);
                window.__pwMetrics['dom-interactive'] = Math.round(entry.domInteractive);
                window.__pwMetrics['dom-content-loaded'] = Math.round(entry.domContentLoadedEventEnd);
                window.__pwMetrics['load-duration'] = Math.round(entry.loadEventEnd);
                window.__pwMetrics['encoded-body-size'] = Math.round(entry.encodedBodySize);
                window.__pwMetrics['decoded-body-size'] = Math.round(entry.decodedBodySize);
            }
        }
    }).observe({ type: 'navigation', buffered: true });

    new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
            window.__pwMetrics[entry.name] = entry.startTime;
        }
    }).observe({ type: 'paint', buffered: true });

    new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
            window.__pwMetrics['largest-contentful-paint'] = entry.startTime;
        }
    }).observe({ type: 'largest-contentful-paint', buffered: true });

    let shifts = [];

    new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
            if (!entry.hadRecentInput) {
                shifts.push(entry);
            }
        }

        window.__pwMetrics['cumulative-layout-shift'] = calculateCLS(shifts).toString();
    }).observe({ type: 'layout-shift', buffered: true });
})();

function calculateCLS(entries) {
    let cls = 0;
    let sessionValue = 0;
    let sessionStart = 0;
    let sessionEnd = 0;

    for (const entry of entries) {
        if (sessionStart === 0 || entry.startTime - sessionEnd > 1000 || entry.startTime - sessionStart > 5000) {
            sessionStart = entry.startTime;
            sessionValue = entry.value;
        } else {
            sessionValue += entry.value;
        }

        sessionEnd = entry.startTime;
        cls = Math.max(cls, sessionValue);
    }

    return cls;
}
