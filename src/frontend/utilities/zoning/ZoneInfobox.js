// utilities/ZoneInfobox.js
export function generateZoneDescription(zoneName, zoneData) {
  if (!zoneData) {
    return `
      <div style="background-color:#1a1a1a; color:#ffffff; font-family:Arial; padding:10px; margin:-10px; width:calc(100% + 20px);">
        <h3 style="margin-top:0; color:#ffffff;">Zone: ${zoneName}</h3>
        <p>No data available for this zone. Right Click on Zone: Settings >> Click "Refresh Zone Data" in the settings panel to load data.</p>
      </div>
    `;
  }

  // Count data items
  const vesselCount = zoneData.vessels ? zoneData.vessels.length : 0;
  const stationCount = zoneData.stations ? zoneData.stations.length : 0;
  const weatherDataCount = zoneData.weather ? zoneData.weather.length : 0;
  const oceanDataCount = zoneData.oceanography
    ? zoneData.oceanography.length
    : 0;
  const alertCount = zoneData.alerts ? zoneData.alerts.length : 0;

  // Create vessel list (limited to first 10)
  let vesselList = "";
  if (vesselCount > 0) {
    const vesselItems = zoneData.vessels
      .slice(0, 10)
      .map((vessel) => {
        const vesselName = vessel.vessel_name || "Unknown";
        const vesselType = vessel.type || "Unknown";
        return `<li>${vesselName} (${vesselType})</li>`;
      })
      .join("");

    vesselList = `
      <div style="margin-top:10px;">
        <h4 style="color:#ffffff; margin-bottom:5px;">Vessels in this zone${
          vesselCount > 10 ? " (showing first 10)" : ""
        }:</h4>
        <ul style="color:#ffffff; padding-left:20px;">
          ${vesselItems}
        </ul>
      </div>
    `;
  }

  return `
    <div style="background-color:#1a1a1a; color:#ffffff; font-family:Arial; padding:10px; margin:-10px; width:calc(100% + 20px);">
      <h3 style="margin-top:0; color:#ffffff;">Zone Details: ${zoneName}</h3>
      <table style="width:100%; color:#ffffff;">
        <tr>
          <td style="color:#ffffff; padding:3px 0;">Vessels:</td>
          <td style="color:#ffffff; padding:3px 0;"><strong>${vesselCount}</strong></td>
        </tr>
        <tr>
          <td style="color:#ffffff; padding:3px 0;">Weather Stations:</td>
          <td style="color:#ffffff; padding:3px 0;">${stationCount}</td>
        </tr>
        <tr>
          <td style="color:#ffffff; padding:3px 0;">Weather Data:</td>
          <td style="color:#ffffff; padding:3px 0;">${weatherDataCount}</td>
        </tr>
        <tr>
          <td style="color:#ffffff; padding:3px 0;">Ocean Data:</td>
          <td style="color:#ffffff; padding:3px 0;">${oceanDataCount}</td>
        </tr>
        <tr>
          <td style="color:#ffffff; padding:3px 0;">Alerts:</td>
          <td style="color:#ffffff; padding:3px 0;">${alertCount}</td>
        </tr>
      </table>
      ${vesselList}
    </div>
  `;
}
