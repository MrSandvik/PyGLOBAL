$(document).ready(function () {

    function renderAnimation(data) {
        var layers = data.piskel.layers;

        // Parse each layer JSON string and decode base64 image data
        layers = layers.map(function (layerStr) {
            var layer = JSON.parse(layerStr);
            layer.image = new Image();
            layer.image.src = layer.chunks[0].base64PNG;
            return layer;
        });

        // Create a canvas element to display the animation
        var canvas = $('<canvas>').attr('width', data.piskel.width).attr('height', data.piskel.height);
        $('body').append(canvas);

        // Render each frame of the animation with the specified layers
        var currentFrame = 0;
        var visibleLayers = [6, 2]; // Change this to specify which layers to display
        setInterval(function () {
            var ctx = canvas[0].getContext('2d');
            ctx.clearRect(0, 0, canvas.width(), canvas.height());

            for (var i = 0; i < visibleLayers.length; i++) {
                var layerIndex = visibleLayers[i];
                var layer = layers[layerIndex];
                var frameIndex = layer.chunks[0].layout[currentFrame][0];
                ctx.drawImage(layer.image, frameIndex * data.piskel.width, 0, data.piskel.width, data.piskel.height, 0, 0, data.piskel.width, data.piskel.height);
            }

            currentFrame = (currentFrame + 1) % layers[0].frameCount;
        }, 1000 / data.piskel.fps);
    }

    async function loadPiskelJson() {
        try {
            const response = await fetch('lcp1.piskel', {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const piskelJson = await response.json();
            renderAnimation(piskelJson);
        } catch (error) {
            console.error('Error fetching Piskel JSON:', error);
        }
    }

    loadPiskelJson();
});
