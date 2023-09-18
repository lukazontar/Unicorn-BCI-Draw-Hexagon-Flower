const bigTriangleSide = 350; // Big equilateral triangle side size
const nTrianglesBottom = 7; // Number of smaller equilateral triangles within the bigger equilateral triangle
const triangleSide = bigTriangleSide / nTrianglesBottom; // Size of smaller triangle side
const triangleHeight = triangleSide * Math.sqrt(3) / 2; // Height of smaller triangle

// Canvas settings
const widthViewBox = bigTriangleSide * 2.5;
const heightViewBox = bigTriangleSide * 2.5;
const width = bigTriangleSide * 2.5;
const height = bigTriangleSide * 2.5;
const viewBox = 0 + " " + 0 + " " + width + " " + height;
const svgns = "http://www.w3.org/2000/svg";

// Drawing origin
const xStart = width / 2 - 75;
const yStart = height / 2 - 75;


/* FUNCTION: formatString
* Helper function to write more beautiful code by formatting strings in a more efficient manner.
* */
function formatString(string, params) {
    // Takes an array of params and inputs them in the main string.
    return string.replace(/{(\d+)}/g, (match, index) => {
        return typeof params[index] !== 'undefined' ? params[index] : match;
    });
}

/* FUNCTION: mapColorToHex
* Helper function to map color from text to HEX code to more beautiful color versions.
* */
function mapColorToHex(colorString) {
    // Red color
    if (colorString === 'red')
        return '#dc3545'
    if (colorString === 'green')
        return '#198754'
    if (colorString === 'blue')
        return '#0d6efd'
    return '#ffffff'
}


/* FUNCTION: drawCanvas
* Draws canvas (hexagon flower) from board state JSON data.
* */
function drawTriangle(g, xStartTriangle, yStartTriangle, triangleSide, triangleHeight, color, phi, ixTriangle, lastIxTriangle) {
    let xPoint1 = xStartTriangle
    let yPoint1 = yStartTriangle
    let xPoint2 = xStartTriangle + triangleSide
    let yPoint2 = yStartTriangle
    let xPoint3 = xStartTriangle + triangleSide / 2
    let yPoint3 = yStartTriangle + triangleHeight
    // Draw triangle with given points
    const triangle = document.createElementNS(svgns, "polygon");
    const points = formatString("{0},{1} {2},{3} {4},{5}", [xPoint1, yPoint1, xPoint2, yPoint2, xPoint3, yPoint3]);

    // Append triangle to SVG group
    triangle.setAttributeNS(null, "points", points);
    triangle.setAttributeNS(null, "fill", color);
    triangle.setAttributeNS(null, "stroke", "#333333");

    // Emphasize last colored triangles
    if (ixTriangle.toString() === lastIxTriangle)
        triangle.setAttributeNS(null, "stroke-width", "4");

    // Draw text -> triangle index
    let triangleIxText = document.createElementNS(svgns, "text");
    const triangleIxTextX = xStartTriangle + Math.abs(triangleHeight) / 1.65;
    const triangleIxTextY = yStartTriangle + triangleHeight / 3;
    const triangleIxTextPhi = 360 - phi;

    triangleIxText.setAttributeNS(null, "x", triangleIxTextX);
    triangleIxText.setAttributeNS(null, "y", triangleIxTextY);
    triangleIxText.setAttributeNS(null, "style", 'font-weight: bold;');
    triangleIxText.setAttributeNS(null, "transform", formatString("rotate({0}, {1}, {2})", [triangleIxTextPhi, triangleIxTextX, triangleIxTextY]));
    triangleIxText.setAttributeNS(null, "dominant-baseline", 'middle');
    triangleIxText.setAttributeNS(null, "text-anchor", 'middle');
    triangleIxText.setAttributeNS(null, "fill", '#333333');

    let textNode = document.createTextNode(ixTriangle);
    triangleIxText.appendChild(textNode);

    g.appendChild(triangle);
    if (phi === 480)
        g.appendChild(triangleIxText);
}

/* FUNCTION: drawCanvas
* Draws canvas (hexagon flower) from board state JSON data.
* */
function drawCanvas(boardState) {
    // Initialize canvas with view box, width and height
    const canvas = document.getElementById("canvas");
    canvas.innerHTML = ""
    canvas.setAttribute("viewBox", viewBox);
    canvas.setAttribute("width", widthViewBox);
    canvas.setAttribute("height", heightViewBox);

    // Last triangle colored index
    const lastTriangleColoredIx = boardState['last_ix_triangle_colored']
    // Rotate the equilateral triangle and generate a hexagon flower by drawing 6 rotated equilateral triangles.
    for (let phi = 0; phi <= 360; phi += 60) {
        // Map phi to first bottom triangle so that we start there.
        const phiMapped = phi + 120
        // Group equilateral triangle into a group of SVG polygons that will be rotated together around xStart and yStart
        const g = document.createElementNS(svgns, "g");
        g.setAttributeNS(null, "id", "g" + phiMapped);
        g.setAttribute('style', "transform: rotate(" + phiMapped + "deg); transform-origin: " + xStart + "px " + yStart + "px;");

        // Initialize starting y for triangles and triangle index to gather data from board state JSON data.
        let ixTriangle = 0
        let yStartTriangle = yStart;

        // Go over all rows of triangles
        for (let i = nTrianglesBottom; i >= 1; i--) {

            // Initialize starting z for drawing triangles (depends on row that we are drawing)
            let xStartTriangle = xStart + (nTrianglesBottom - i) * triangleSide / 2

            // Go over all columns of triangles
            for (let j = nTrianglesBottom - (nTrianglesBottom - i); j >= 1; j--) {

                // Map color to HEX
                let colorTriangle = mapColorToHex(boardState['triangles'][ixTriangle]['color'])

                // Draw triangle with upward orientation
                drawTriangle(g,
                    xStartTriangle,
                    yStartTriangle,
                    triangleSide,
                    -triangleHeight,
                    colorTriangle,
                    phiMapped,
                    ixTriangle,
                    lastTriangleColoredIx
                )

                // After drawing a triangle, we must increase the index so that we show correct data from board state JSON.
                ixTriangle++;

                // For bottom row, we don't want to draw downward facing triangles.
                if (i !== nTrianglesBottom) {

                    // Map color to HEX
                    let colorTriangle = mapColorToHex(boardState['triangles'][ixTriangle]['color'])

                    // Draw triangle with downward orientation
                    // For downward oriented triangle change y of 3rd point
                    drawTriangle(g,
                        xStartTriangle,
                        yStartTriangle,
                        triangleSide,
                        +triangleHeight,
                        colorTriangle,
                        phiMapped,
                        ixTriangle,
                        lastTriangleColoredIx
                    )

                    // After drawing a triangle, we must increase the index so that we show correct data from board state JSON.
                    ixTriangle++;
                }
                // Update starting x for drawing triangles (for next column)
                xStartTriangle += triangleSide;
            }
            // Update starting y for drawing triangles (for next row)
            yStartTriangle -= triangleHeight;
        }

        // Append SVG group to SVG canvas
        canvas.appendChild(g);
    }
}


/* FUNCTION: colorTriangle
* Generates a request to REST API to save and draw a colored triangle using the personal ID to generate the triangle index.
* */
function colorTriangle(that) {
    // Get personal ID
    let personalId = document.getElementById("personalId").value;

    // Get color
    let color = null;
    if (document.getElementById("greenColor").checked)
        color = 'green';
    if (document.getElementById("blueColor").checked)
        color = 'blue';
    if (document.getElementById("redColor").checked)
        color = 'red';

    // Validation checks on inputs
    if (color === null) {
        alert('Please select a color.');
    } else if (personalId === null || personalId === '') {
        alert('Please enter your personal ID.');
    } else {
        // If validation checks went through, color a triangle and redraw canvas.
        let xmlHttp = new XMLHttpRequest();
        xmlHttp.open("GET", 'http://127.0.0.1:8000/api/colorTriangle?personalId=' + personalId + '&color=' + color, false);
        xmlHttp.send(null);

        const response_json = JSON.parse(xmlHttp.responseText);
        if (response_json.hasOwnProperty('error')) {
            document.getElementById('modalErrorText').innerHTML = response_json['error'];
            $('#modalError').modal('toggle');
        } else {
            drawCanvas(response_json);

            // Show modal window that explains the user how triangle position was calculated.
            document.getElementById('modalEquationPersonalIdText').innerHTML = 'Personal ID:  <b>' + personalId + '</b>';
            document.getElementById('modalEquationText').innerHTML = '<b>' + response_json['last_equation'] + '</b>';
            document.getElementById('modalEquationResult').innerHTML = 'Triangle colored: <b>' + response_json['last_ix_triangle_colored'] + '</b>';
            $('#modalEquation').modal('toggle');
        }
    }
}


/* FUNCTION: initCanvas
* Initialize canvas with current (last modified) board state JSON retrievable through API request.
* If number of triangles changed or no current state exists, it initializes a new board state with cleared settings.
* */
function initCanvas() {
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", 'http://127.0.0.1:8000/api/initCanvas?nTrianglesBottom=' + nTrianglesBottom, false);
    xmlHttp.send(null);

    const response_json = JSON.parse(xmlHttp.responseText);
    if (response_json.hasOwnProperty('error')) {
        document.getElementById('modalErrorText').innerHTML = response_json['error'];
        $('#modalError').modal('toggle');
    } else {
        drawCanvas(response_json);
    }
}


/* FUNCTION: saveCanvas
* Saves the image (.png) of current state of the generated hexagon flower art.
* */
function saveCanvas() {
    var svg = document.getElementById('canvas');
    // get svg data
    var xml = new XMLSerializer().serializeToString(svg);

    // make it base64
    var svg64 = btoa(xml);
    var b64Start = 'data:image/svg+xml;base64,';

    // prepend a "header"
    var image64 = b64Start + svg64;

    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", 'http://127.0.0.1:8000/api/saveCanvas', false);

    xmlHttp.send('{"data": "' + image64 + '"}');
}


/* To communicate with a brain-computer interface, we push brain-computer
* interface data through a TCP connection and set up a listener on the
* REST API server to save new data as it arrives.
* To propagate this data in a frequent manner to this user interface,
* we establish a polling system that requests data update every second.
* */
window.setInterval(function () {
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", 'http://127.0.0.1:8000/api/readBrainInterfaceData', true);
    xmlHttp.onload = function () {
        // If request was successful, fill inputs.
        if (this.status >= 200 && this.status < 300) {
            let response = JSON.parse(xmlHttp.response)


            if (response.hasOwnProperty('confirm') && response['confirm']) {
                let xmlHttpColorTriangle = new XMLHttpRequest();
                xmlHttpColorTriangle.open("GET", 'http://127.0.0.1:8000/api/colorTriangle?personalId=' + response['personal_id'] + '&color=' + response['color'], false);
                xmlHttpColorTriangle.send(null);

                const response_json = JSON.parse(xmlHttpColorTriangle.responseText);
                drawCanvas(response_json);
                saveCanvas();
            } else {
                let xmlHttpColorTriangle = new XMLHttpRequest();
                xmlHttpColorTriangle.open("GET", 'http://127.0.0.1:8000/api/readBoardStateData', false);
                xmlHttpColorTriangle.send(null);

                const response_json = JSON.parse(xmlHttpColorTriangle.responseText);

                drawCanvas(response_json);
            }
        } else {
            // Print error.
            console.log({
                status: this.status,
                statusText: xmlHttp.statusText
            });
        }
    };


    xmlHttp.send();
}, 1000)