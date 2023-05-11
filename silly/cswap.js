function hexToRGBA(hex) {
    const bigint = parseInt(hex.slice(1), 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    const a = 255;

    return { r, g, b, a };
}

async function replaceColors(base64Image, colorPairs) {
    const image = new Image();
    image.src = base64Image;

    return new Promise((resolve) => {
        image.onload = function () {
            const canvas = document.createElement('canvas');
            canvas.width = image.width;
            canvas.height = image.height;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(image, 0, 0, image.width, image.height);

            const imageData = ctx.getImageData(0, 0, image.width, image.height);
            const data = imageData.data;

            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                const a = data[i + 3];

                for (const pair of colorPairs) {
                    const oldColor = hexToRGBA(pair[0]);
                    const newColor = hexToRGBA(pair[1]);

                    if (r === oldColor.r && g === oldColor.g && b === oldColor.b && a === oldColor.a) {
                        data[i] = newColor.r;
                        data[i + 1] = newColor.g;
                        data[i + 2] = newColor.b;
                        data[i + 3] = newColor.a;
                    }
                }
            }

            ctx.putImageData(imageData, 0, 0);
            resolve(canvas.toDataURL());
        };
    });
}
