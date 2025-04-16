() => {
    const timing = performance.timing;
    const navStart = timing.navigationStart;
    const TTFB = timing.responseStart - navStart;

    return {
        ...window.__pwMetrics,
        TTFB,
        loadTime: timing.loadEventEnd - navStart,
        domContentLoaded: timing.domContentLoadedEventEnd - navStart,
    };
};
