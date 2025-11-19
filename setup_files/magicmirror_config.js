var config = {
    address: "0.0.0.0", 
    port: 8080,
    ipWhitelist: [], 
    language: "en",
    modules: [
        	{
        module: 'MMM-Remote-Control',
        // Unsecured for localhost access (safe for this appliance)
        config: {
            customCommand: {},
            showModuleApiMenu: true,
            secureEndpoints: false,
        	}
    	},
	{
            module: "MMM-BackgroundSlideshow",
            position: "fullscreen_below",
            config: {
                imagePaths: ["/home/ppcpi/display_controller/media/family_photos/"],
                transitionImages: true,
                randomizeImageOrder: true,
                slideshowSpeed: 900000, // 15 minutes
                transitionSpeed: "1s",
                backgroundSize: "contain"
            }
        }
    ]
};
if (typeof module !== "undefined") {module.exports = config;}
