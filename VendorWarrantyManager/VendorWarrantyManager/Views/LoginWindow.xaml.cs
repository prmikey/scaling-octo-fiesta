using System;
using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using VendorWarrantyManager.Models;
using VendorWarrantyManager.Services;

namespace VendorWarrantyManager.Views
{
    public partial class LoginWindow : Window
    {
        public LoginWindow()
        {
            InitializeComponent();
        }

        private async void LoginButton_Click(object sender, RoutedEventArgs e)
        {
            // Validate inputs
            if (string.IsNullOrWhiteSpace(UsernameTextBox.Text))
            {
                ShowError("Please enter a username");
                return;
            }

            if (string.IsNullOrWhiteSpace(PasswordBox.Password))
            {
                ShowError("Please enter a password");
                return;
            }

            // Get selected vendor
            var vendorIndex = VendorComboBox.SelectedIndex;
            var vendorType = vendorIndex == 0 ? VendorType.Dell : VendorType.Lenovo;

            // Show loading
            LoadingPanel.Visibility = Visibility.Visible;
            ErrorTextBlock.Visibility = Visibility.Collapsed;
            IsEnabled = false;

            try
            {
                // Get appropriate service
                IVendorApiService? apiService = vendorType == VendorType.Dell
                    ? App.ServiceProvider?.GetService<DellApiService>()
                    : App.ServiceProvider?.GetService<LenovoApiService>();

                if (apiService == null)
                {
                    ShowError("Failed to initialize API service");
                    return;
                }

                // Authenticate
                bool success = await apiService.AuthenticateAsync(
                    UsernameTextBox.Text,
                    PasswordBox.Password
                );

                if (success)
                {
                    // Create credentials object
                    var credentials = new UserCredentials
                    {
                        Vendor = vendorType,
                        Username = UsernameTextBox.Text,
                        Password = PasswordBox.Password
                    };

                    // Open dashboard
                    var dashboard = new DashboardWindow(credentials, apiService);
                    dashboard.Show();
                    this.Close();
                }
                else
                {
                    ShowError("Authentication failed. Please check your credentials.");
                }
            }
            catch (Exception ex)
            {
                ShowError($"Login error: {ex.Message}");
            }
            finally
            {
                LoadingPanel.Visibility = Visibility.Collapsed;
                IsEnabled = true;
            }
        }

        private void ShowError(string message)
        {
            ErrorTextBlock.Text = message;
            ErrorTextBlock.Visibility = Visibility.Visible;
        }
    }
}
