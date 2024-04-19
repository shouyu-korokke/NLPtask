using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.Web.WebView2.Core;
using System;
using System.Globalization;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media;
using System.Diagnostics;
namespace NLP
{
    public partial class MainWindow : Window
    {
        private readonly GeocodingService geocodingService = new GeocodingService();
        private bool webViewReady = false;
        private List<AccidentRecord> _allAccidents = new List<AccidentRecord>();


        public MainWindow()
        {
            InitializeComponent();
            InitializeAsync();
            AccidentsListView.ItemsSource = _allAccidents;
        }
        private async void FilterButton_Click(object sender, RoutedEventArgs e)
        {
            if (startDatePicker.SelectedDate == null || endDatePicker.SelectedDate == null)
            {
                MessageBox.Show("Please select both start and end dates.");
                return;
            }
            DateTime startDate = startDatePicker.SelectedDate.Value;
            DateTime endDate = endDatePicker.SelectedDate.Value;

            if (startDate > endDate)
            {
                MessageBox.Show("Start date must be before end date.");
                return;
            }
           // MessageBox.Show($"Filtering from {startDatePicker.SelectedDate} to {endDatePicker.SelectedDate}", "Filtering", MessageBoxButton.OK);
            string format = "MMMM d, yyyy, hh:mm tt";
            var filteredAccidents = _allAccidents.Where(accident =>
                DateTime.ParseExact(accident.PublicationDate, format, CultureInfo.InvariantCulture) >= startDate.Date &&
                DateTime.ParseExact(accident.PublicationDate, format, CultureInfo.InvariantCulture) <= endDate.Date).ToList();

            AccidentsListView.ItemsSource = filteredAccidents;    // Now update the map
            await UpdateMapWithFilteredAccidents(filteredAccidents);
        }
        private async Task UpdateMapWithFilteredAccidents(List<AccidentRecord> filteredAccidents)
        {
            if (!webViewReady) return;

            // Clear existing markers
            await webView.CoreWebView2.ExecuteScriptAsync("clearMarkers();");

            // Add new markers for filtered accidents
            foreach (var record in filteredAccidents)
            {
                var location = record.MetaLocation;
                var (lat, lng) = await geocodingService.GeocodeLocationAsync(location);
                if (lat != 0 && lng != 0) // Assuming geocoding service returns (0, 0) for invalid locations
                {
                    var script = $"addAccidentMarker({lat}, {lng}, '{EscapeJsString(record.Title)}', '{EscapeJsString(record.RawText)}');";
                    await webView.CoreWebView2.ExecuteScriptAsync(script);
                }
            }
        }

        private async void InitializeAsync()
        {
            await webView.EnsureCoreWebView2Async(null);
            webView.NavigationCompleted += WebView_NavigationCompleted;
            string path = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "MapPage.html");
            webView.CoreWebView2.Navigate($"file:///{path.Replace("\\", "/")}");
        }
        private async void WebView_NavigationCompleted(object sender, CoreWebView2NavigationCompletedEventArgs e)
        {
            if (e.IsSuccess)
            {
                webViewReady = true;
                await LoadAccidentDataAsync();
            }
            else
            {
                MessageBox.Show("Failed to load the map page.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async Task LoadAccidentDataAsync()
        {
            if (!webViewReady) return;
            //
           // string filePath = @"C:\Users\josef\source\repos\NLP\NLP\accidents_data.csv";
            string filePath = @"C:\Users\liu chang\Downloads\NLP_2\NLP\NLP\accidents_data.csv";
            try
            {
                var config = new CsvConfiguration(CultureInfo.InvariantCulture)
                {
                    Delimiter = ";",
                };
                using (var reader = new StreamReader(filePath))
                using (var csv = new CsvReader(reader, config))
                {
                    // Register the mapping class with the CsvReader instance.
                    csv.Context.RegisterClassMap<AccidentRecordMap>();

                    var records = csv.GetRecords<AccidentRecord>().ToList(); // Reading the records as strongly-typed objects
                    _allAccidents.AddRange(records);
                    foreach (var record in records)
                    {
                        // Now you can directly access properties of AccidentRecord
                        var location = record.MetaLocation;

                        // Perform geocoding based on the MetaLocation property
                        var (lat, lng) = await geocodingService.GeocodeLocationAsync(location);

                        if (lat != 0 && lng != 0) // Check for valid coordinates
                        {
                            var script = $"addAccidentMarker({lat}, {lng}, '{EscapeJsString(record.Title)}', '{EscapeJsString(record.RawText)}');";
                            await webView.CoreWebView2.ExecuteScriptAsync(script);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to load accident data: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private string EscapeJsString(string value)
        {
            // Escapes JavaScript string to prevent breaking the script.
            return value.Replace("'", "\\'").Replace(Environment.NewLine, "\\n");
        }

        private async void Window_Loaded(object sender, RoutedEventArgs e)
        {
            await LoadAccidentDataAsync(); // This method will be called when the window is fully loaded.
        }

        private async void ProcessButtonClick(object sender, RoutedEventArgs e)
        {
            string pythonExecutable = @"C:\Python311\python.exe"; // Path to the Python executable
            string scriptPath = @"C:\Users\liu chang\urlAcquisition.py"; // Path to your Python script
            string url = UrlTextBox.Text; // Assuming UrlTextBox is the TextBox where the URL is entered

            if (string.IsNullOrWhiteSpace(url))
            {
                MessageBox.Show("Please enter a URL.");
                return;
            }

            string arguments = $"\"{scriptPath}\" \"{url}\""; // Arguments to pass to the Python script
            try
            {
                using (Process process = new Process())
                {
                    process.StartInfo = new ProcessStartInfo(pythonExecutable, arguments)
                    {
                        RedirectStandardOutput = true,
                        UseShellExecute = false,
                        CreateNoWindow = true,
                    };
                    process.StartInfo.RedirectStandardError = true;
                    process.Start();
                    string errors = await process.StandardError.ReadToEndAsync();
                    if (!string.IsNullOrEmpty(errors))
                    {
                        MessageBox.Show("Python stderr: " + errors);
                    }

                    // Reading the output of the script
                    string output = await process.StandardOutput.ReadToEndAsync();
                    process.WaitForExit();
                    // For debugging
                    //MessageBox.Show("output:" + output);

                    if (!string.IsNullOrWhiteSpace(output))
                    {
                        try
                        {
                            var accidentInfo = System.Text.Json.JsonSerializer.Deserialize<AccidentRecord>(output);
                            // Now update the ListView and the map with this info
                            if (accidentInfo != null)
                            {
                                AccidentsListView.ItemsSource = new List<AccidentRecord>{accidentInfo};
                                await UpdateMapWithFilteredAccidents(new List<AccidentRecord> { accidentInfo });
                            }
                            else
                            {
                                MessageBox.Show("The deserialized accident info is null.");
                            }
                        }
                        catch (System.Text.Json.JsonException jsonEx)
                        {
                            // Handle JSON parsing error
                            MessageBox.Show($"JSON parsing error: {jsonEx.Message}");
                        }
                    }
                    else
                    {
                        MessageBox.Show("No output received from the script.");
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred: {ex.Message}");
            }
        }
    }
}