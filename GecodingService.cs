using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Http;
using System.Text.Json;
using System.Globalization;

namespace NLP
{
    public class GeocodingService
    {
        private static readonly HttpClient httpClient = new HttpClient();

        public GeocodingService()
        {
            // Nominatim requires a unique User-Agent header for requests
            httpClient.DefaultRequestHeaders.UserAgent.ParseAdd("nlp/1.0 (yusifden@gmail.com)");
        }

        public async Task<(double lat, double lng)> GeocodeLocationAsync(string location)
        {
            try
            {
                string requestUri = $"https://nominatim.openstreetmap.org/search?format=json&q={Uri.EscapeDataString(location)}";
                var response = await httpClient.GetAsync(requestUri);
                if (response.IsSuccessStatusCode)
                {
                    string responseBody = await response.Content.ReadAsStringAsync();
                    var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                    var locations = JsonSerializer.Deserialize<List<LocationResponse>>(responseBody, options);
                    if (locations != null && locations.Count > 0)
                    {
                        // Parse the latitude and longitude as doubles
                        var lat = double.Parse(locations[0].Lat, CultureInfo.InvariantCulture);
                        var lon = double.Parse(locations[0].Lon, CultureInfo.InvariantCulture);
                        return (lat, lon);
                    }
                }
            }
            catch (Exception e)
            {
                // Consider logging the exception details to understand what went wrong
                Console.WriteLine($"Exception in geocoding request: {e.Message}");
            }

            return (0, 0); // Return (0, 0) if parsing fails or if no data could be retrieved
        }


        private class LocationResponse
        {
            public string Lat { get; set; }
            public string Lon { get; set; }
        }

    }
}
