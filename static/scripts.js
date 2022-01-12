document.addEventListener('DOMContentLoaded', function() {
    // Palette from https://coolors.co/
    let colors = ["bbdef0","00a6a6","efca08","f49f0a","f08700"];

    let cells = document.querySelectorAll(".heatmap");
    for (let cell of cells) {
        let mins = Number(cell.getAttribute("data-mins"));
        
        let zone = Math.floor(mins / 60);

        if (zone >= colors.length) {
            zone = colors.length - 1;
        }

        cell.style.backgroundColor = "#" + colors[zone];
    }
});