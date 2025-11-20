using System;
using System.Windows;
using System.Windows.Media;
using VendorWarrantyManager.Services;

namespace VendorWarrantyManager.Views
{
    public partial class WarrantyCheckerWindow : Window
    {
        private readonly IVendorApiService _apiService;

        public WarrantyCheckerWindow(IVendorApiService apiService)
        {
            InitializeComponent();
            _apiService = apiService;
        }

        private async void CheckWarrantyButton_Click(object sender, RoutedEventArgs e)
        {
            var serviceTag = ServiceTagTextBox.Text.Trim();

            if (string.IsNullOrWhiteSpace(serviceTag))
            {
                MessageBox.Show("Please enter a service tag", "Validation",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            try
            {
                // Show loading
                LoadingPanel.Visibility = Visibility.Visible;
                NoResultsTextBlock.Visibility = Visibility.Collapsed;
                ResultsPanel.Visibility = Visibility.Collapsed;

                // Check warranty
                var warrantyInfo = await _apiService.CheckWarrantyAsync(serviceTag);

                // Hide loading
                LoadingPanel.Visibility = Visibility.Collapsed;

                if (warrantyInfo.IsValid)
                {
                    // Show results
                    ResultsPanel.Visibility = Visibility.Visible;

                    ServiceTagResult.Text = warrantyInfo.ServiceTag;
                    ProductNameResult.Text = warrantyInfo.ProductName;
                    ServiceLevelResult.Text = warrantyInfo.ServiceLevel ?? "N/A";
                    StartDateResult.Text = warrantyInfo.StartDate?.ToString("MM/dd/yyyy") ?? "N/A";
                    EndDateResult.Text = warrantyInfo.EndDate?.ToString("MM/dd/yyyy") ?? "N/A";
                    WarrantyStatusResult.Text = warrantyInfo.Status;

                    // Update status indicator
                    if (warrantyInfo.EndDate.HasValue && warrantyInfo.EndDate.Value >= DateTime.Now)
                    {
                        StatusTextBlock.Text = "✓ Warranty is Active";
                        StatusBorder.Background = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#E8F5E9"));
                        StatusTextBlock.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#2E7D32"));
                    }
                    else
                    {
                        StatusTextBlock.Text = "✗ Warranty Expired";
                        StatusBorder.Background = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FFEBEE"));
                        StatusTextBlock.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#C62828"));
                    }
                }
                else
                {
                    NoResultsTextBlock.Text = "No warranty information found for this service tag";
                    NoResultsTextBlock.Visibility = Visibility.Visible;
                }
            }
            catch (Exception ex)
            {
                LoadingPanel.Visibility = Visibility.Collapsed;
                MessageBox.Show($"Error checking warranty: {ex.Message}", "Error",
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }
    }
}
