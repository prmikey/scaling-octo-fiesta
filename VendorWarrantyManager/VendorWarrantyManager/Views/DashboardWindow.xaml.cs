using System;
using System.Collections.Generic;
using System.Windows;
using VendorWarrantyManager.Models;
using VendorWarrantyManager.Services;

namespace VendorWarrantyManager.Views
{
    public partial class DashboardWindow : Window
    {
        private readonly UserCredentials _credentials;
        private readonly IVendorApiService _apiService;
        private string? _currentFilter;

        public DashboardWindow(UserCredentials credentials, IVendorApiService apiService)
        {
            InitializeComponent();
            _credentials = credentials;
            _apiService = apiService;

            // Set user info
            TitleTextBlock.Text = $"{credentials.Vendor} Dashboard";
            UserInfoTextBlock.Text = $"Logged in as: {credentials.Username}";

            // Load claims
            LoadClaimsAsync();
        }

        private async void LoadClaimsAsync(string? filterByUser = null)
        {
            try
            {
                LoadingPanel.Visibility = Visibility.Visible;
                NoClaimsTextBlock.Visibility = Visibility.Collapsed;
                ClaimsDataGrid.Visibility = Visibility.Collapsed;

                var claims = await _apiService.GetClaimsAsync(filterByUser);

                LoadingPanel.Visibility = Visibility.Collapsed;

                if (claims.Count == 0)
                {
                    NoClaimsTextBlock.Visibility = Visibility.Visible;
                }
                else
                {
                    ClaimsDataGrid.ItemsSource = claims;
                    ClaimsDataGrid.Visibility = Visibility.Visible;
                }
            }
            catch (Exception ex)
            {
                LoadingPanel.Visibility = Visibility.Collapsed;
                MessageBox.Show($"Error loading claims: {ex.Message}", "Error",
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void ApplyFilterButton_Click(object sender, RoutedEventArgs e)
        {
            var filterUser = FilterUserTextBox.Text.Trim();

            if (string.IsNullOrWhiteSpace(filterUser))
            {
                MessageBox.Show("Please enter a username to filter", "Validation",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            _currentFilter = filterUser;
            LoadClaimsAsync(filterUser);
        }

        private void ClearFilterButton_Click(object sender, RoutedEventArgs e)
        {
            FilterUserTextBox.Clear();
            _currentFilter = null;
            LoadClaimsAsync();
        }

        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            LoadClaimsAsync(_currentFilter);
        }

        private void WarrantyCheckerButton_Click(object sender, RoutedEventArgs e)
        {
            var warrantyChecker = new WarrantyCheckerWindow(_apiService);
            warrantyChecker.Owner = this;
            warrantyChecker.ShowDialog();
        }

        private void MakeClaimButton_Click(object sender, RoutedEventArgs e)
        {
            var claimMaker = new ClaimMakerWindow(_credentials, _apiService);
            claimMaker.Owner = this;

            if (claimMaker.ShowDialog() == true)
            {
                // Refresh claims list after successful claim creation
                LoadClaimsAsync(_currentFilter);
            }
        }

        private void LogoutButton_Click(object sender, RoutedEventArgs e)
        {
            var result = MessageBox.Show("Are you sure you want to logout?", "Logout",
                MessageBoxButton.YesNo, MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                var loginWindow = new LoginWindow();
                loginWindow.Show();
                this.Close();
            }
        }
    }
}
