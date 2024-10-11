function onScanSuccess(decodedText, decodedResult) {
    console.log(`Code scanned = ${decodedText}`, decodedResult);

    // Display the barcode result
    document.getElementById("result").innerHTML = `Barcode detected: ${decodedText}`;

    // Send the barcode to the Flask server
    axios.post('/send_barcode', {
        barcode: decodedText
    })
    .then(function (response) {
        if (response.data.details) {
            let details = response.data.details;
            document.getElementById("result").innerHTML = `
                Barcode: ${response.data.label} <br>
                Product: ${details.product_name} <br>
                Price: ${details.price} <br>
                Size: ${details.size_name} <br>
                Sale Price: ${details.sale_price || 'N/A'}
            `;
        } else {
            document.getElementById("result").innerHTML = "Barcode detected, but no matching item found.";
        }
    })
    .catch(function (error) {
        console.error(error);
        document.getElementById("result").innerHTML = "Error: Could not process barcode.";
    });
}

function onScanFailure(error) {
    console.warn(`Code scan error = ${error}`);
}

// Initialize the HTML5 QR Code Scanner with specific camera constraints
function startScanner() {
    let config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        experimentalFeatures: {
            useBarCodeDetectorIfSupported: true
        },
        videoConstraints: {
            facingMode: { exact: "environment" } // Force the use of the rear camera on mobile devices
        }
    };

    let html5QrcodeScanner = new Html5QrcodeScanner("qr-reader", config, /* verbose= */ false);
    html5QrcodeScanner.render(onScanSuccess, onScanFailure);
}

// Start the scanner when the window loads
window.onload = startScanner;
