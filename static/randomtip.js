document.addEventListener("DOMContentLoaded", function() {
    const tips = [
      "Monitor temperature and humidity levels closely to ensure optimal conditions for egg development, adjusting settings as needed for different species.",
      "Regularly turn eggs manually or use an automatic turner to promote even heating and prevent embryo adhesion to the shell.",
      "Keep the incubator clean and sanitized to prevent bacterial contamination and ensure healthy hatching.",
      "Maintain proper ventilation to prevent carbon dioxide buildup and ensure sufficient oxygen supply for developing embryos.",
      "Handle eggs gently during transfer to minimize the risk of damage or chilling, which can negatively impact hatching success.",
      "Document key parameters such as temperature, humidity, and turning schedule to track progress and troubleshoot any issues that arise.",
      "Gradually decrease humidity levels towards the end of incubation to mimic natural conditions and facilitate hatching.",
      "Monitor egg weight loss to gauge moisture loss and adjust humidity levels accordingly for optimal hatch rates.",
      "Avoid opening the incubator unnecessarily to prevent temperature and humidity fluctuations that can disrupt embryo development.",
      "Be prepared for potential emergencies by having backup equipment and an action plan in place for power outages or equipment failures."
    ];
  
    function updateTips() {
      const randomIndexFront = Math.floor(Math.random() * tips.length);
      const randomIndexBack = Math.floor(Math.random() * tips.length);
      document.getElementById("randomTipFront").textContent = tips[randomIndexFront];
      document.getElementById("randomTipBack").textContent = tips[randomIndexBack];
    }
  
    updateTips(); // Call initially
    setInterval(updateTips, 7000); // Call updateTips every 7 seconds
  });
  