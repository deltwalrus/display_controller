var config = {
    address: "0.0.0.0", 
    port: 8080,
    ipWhitelist: [], 
    language: "en",
    modules: [
        {
            module: "MMM-BackgroundSlideshow",
            position: "fullscreen_below",
            config: {
                imagePaths: ["/home/ppcpi/display_controller/media/family_photos/"],
                transitionImages: true,
                randomizeImageOrder: true,
                slideshowSpeed: 900000, // 15 minutes
                transitionSpeed: "1s",
                backgroundSize: "cover"
            }
        }
    ]
};
if (typeof module !== "undefined") {module.exports = config;}
