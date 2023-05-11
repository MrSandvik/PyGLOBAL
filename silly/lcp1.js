function renderAnimation(data, scalingMultiplier, frameDelay, accent1, accent2, hair, skin, outline, bodyLayerName, headLayerName, parentElement, orientation) {
    const defaultColors = {
        accent1: '#c7fe97',
        accent2: '#4156f1',
        hair: '#886600',
        skin: '#ef8982',
        outline: '#000000',
    };

    const colorPairs = [
        accent1 ? [defaultColors.accent1, accent1] : null,
        accent2 ? [defaultColors.accent2, accent2] : null,
        hair ? [defaultColors.hair, hair] : null,
        skin ? [defaultColors.skin, skin] : null,
        outline ? [defaultColors.outline, outline] : null,
    ].filter(Boolean); // Remove any null elements from the array

    var layers = data.piskel.layers;

    // Filter layers based on bodyLayerName and headLayerName
    layers = layers.filter(layer => {
        const layerName = JSON.parse(layer).name;
        return layerName === `Body${bodyLayerName}` || layerName === `Head${headLayerName}`;
    });

    // Parse each layer JSON string and decode base64 image data
    layers = layers.map(async function (layerStr) {
        var layer = JSON.parse(layerStr);
        layer.image = new Image();

        const newBase64Image = await replaceColors(layer.chunks[0].base64PNG, colorPairs);
        layer.image.src = newBase64Image;

        return layer;
    });

    Promise.all(layers).then((processedLayers) => {
        layers = processedLayers;

        // Create a canvas element to display the animation
        var canvas = $('<canvas>').attr('width', data.piskel.width * scalingMultiplier).attr('height', data.piskel.height * scalingMultiplier);
        parentElement.append(canvas);

        // Render each frame of the animation with the specified layers
        var currentFrame = 0;
        setInterval(function () {
            var ctx = canvas[0].getContext('2d');
            ctx.clearRect(0, 0, canvas.width(), canvas.height());
            ctx.imageSmoothingEnabled = false; // Disable image smoothing
            
            if (orientation === 'right') {
                ctx.translate(data.piskel.width * scalingMultiplier, 0);
                ctx.scale(-1, 1);
            }
            ctx.scale(scalingMultiplier, scalingMultiplier);
    
            layers.forEach(layer => {
                var frameIndex = layer.chunks[0].layout[currentFrame][0];
                ctx.drawImage(layer.image, frameIndex * data.piskel.width, 0, data.piskel.width, data.piskel.height, 0, 0, data.piskel.width, data.piskel.height);
            });
    
            ctx.setTransform(1, 0, 0, 1, 0, 0);
            currentFrame = (currentFrame + 1) % layers[0].frameCount;
        }, frameDelay / data.piskel.fps);
    });
}

async function loadPiskelJson(fileName, options = {}) {
    const {
        scalingMultiplier = 1,
        frameDelay = 1000,
        accent1,
        accent2,
        hair,
        skin,
        outline,
        body = '1',
        head = '1',
        orientation = 'left',
    } = options;

    try {
        // Find the preceding div element
        const scriptElement = $('script').last();
        const parentElement = scriptElement.parent();

        const response = await fetch(fileName, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const piskelJson = await response.json();
        renderAnimation(piskelJson, scalingMultiplier, frameDelay, accent1, accent2, hair, skin, outline, body, head, parentElement, orientation);
    } catch (error) {
        console.error('Error fetching Piskel JSON:', error);
    }
}

// Add the function to the global window object
window.loadPiskelJson = loadPiskelJson;