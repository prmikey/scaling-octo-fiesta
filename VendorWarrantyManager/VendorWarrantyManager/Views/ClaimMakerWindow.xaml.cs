using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using Microsoft.Win32;
using VendorWarrantyManager.Models;
using VendorWarrantyManager.Services;

namespace VendorWarrantyManager.Views
{
    public partial class ClaimMakerWindow : Window
    {
        private readonly UserCredentials _credentials;
        private readonly IVendorApiService _apiService;
        private readonly ObservableCollection<ImageItem> _images;
        private const int MAX_IMAGES_DELL = 8;

        public ClaimMakerWindow(UserCredentials credentials, IVendorApiService apiService)
        {
            InitializeComponent();
            _credentials = credentials;
            _apiService = apiService;
            _images = new ObservableCollection<ImageItem>();

            ImagePreviewList.ItemsSource = _images;

            // Show Dell-specific notice if vendor is Dell
            if (credentials.Vendor == VendorType.Dell)
            {
                DellNotice.Visibility = Visibility.Visible;
                VendorInfoTextBlock.Text = "Vendor: Dell Tech Direct (Images required: 1-8)";
            }
            else
            {
                VendorInfoTextBlock.Text = $"Vendor: {credentials.Vendor}";
            }

            UpdateImageCount();
        }

        private void AddImagesButton_Click(object sender, RoutedEventArgs e)
        {
            var isDell = _credentials.Vendor == VendorType.Dell;
            var maxImages = isDell ? MAX_IMAGES_DELL : int.MaxValue;

            if (_images.Count >= maxImages)
            {
                MessageBox.Show($"Maximum {maxImages} images allowed", "Limit Reached",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var openFileDialog = new OpenFileDialog
            {
                Filter = "Image files (*.jpg, *.jpeg, *.png)|*.jpg;*.jpeg;*.png",
                Multiselect = true,
                Title = "Select Images"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                foreach (var fileName in openFileDialog.FileNames)
                {
                    if (_images.Count >= maxImages)
                    {
                        MessageBox.Show($"Maximum {maxImages} images reached. Additional images not added.",
                            "Limit Reached", MessageBoxButton.OK, MessageBoxImage.Information);
                        break;
                    }

                    try
                    {
                        var fileInfo = new FileInfo(fileName);
                        var imageData = File.ReadAllBytes(fileName);

                        // Create thumbnail
                        var bitmap = new BitmapImage();
                        bitmap.BeginInit();
                        bitmap.UriSource = new Uri(fileName);
                        bitmap.DecodePixelWidth = 60;
                        bitmap.CacheOption = BitmapCacheOption.OnLoad;
                        bitmap.EndInit();

                        var imageItem = new ImageItem
                        {
                            FileName = Path.GetFileName(fileName),
                            FilePath = fileName,
                            FileSize = FormatFileSize(fileInfo.Length),
                            ImageData = imageData,
                            ThumbnailSource = bitmap
                        };

                        _images.Add(imageItem);
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Error loading image {fileName}: {ex.Message}",
                            "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }

                UpdateImageCount();
            }
        }

        private void RemoveImageButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is ImageItem imageItem)
            {
                _images.Remove(imageItem);
                UpdateImageCount();
            }
        }

        private void UpdateImageCount()
        {
            var isDell = _credentials.Vendor == VendorType.Dell;
            var maxImages = isDell ? MAX_IMAGES_DELL : "∞";
            ImageCountTextBlock.Text = $"{_images.Count}/{maxImages}";
        }

        private async void SubmitClaimButton_Click(object sender, RoutedEventArgs e)
        {
            // Validation
            if (string.IsNullOrWhiteSpace(ServiceTagTextBox.Text))
            {
                MessageBox.Show("Please enter a service tag", "Validation",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (string.IsNullOrWhiteSpace(DescriptionTextBox.Text))
            {
                MessageBox.Show("Please enter a description", "Validation",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            // Dell-specific validation
            if (_credentials.Vendor == VendorType.Dell)
            {
                if (_images.Count == 0)
                {
                    MessageBox.Show("Dell requires at least one image for claims", "Validation",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                if (_images.Count > MAX_IMAGES_DELL)
                {
                    MessageBox.Show($"Dell allows maximum {MAX_IMAGES_DELL} images per claim", "Validation",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }
            }

            try
            {
                LoadingPanel.Visibility = Visibility.Visible;
                IsEnabled = false;

                // Create claim request
                var request = new CreateClaimRequest
                {
                    ServiceTag = ServiceTagTextBox.Text.Trim(),
                    Description = DescriptionTextBox.Text.Trim(),
                    PartNumber = PartNumberTextBox.Text.Trim(),
                    SerialNumber = SerialNumberTextBox.Text.Trim(),
                    Images = _images.Select(img => img.ImageData).ToList()
                };

                // Submit claim
                var claim = await _apiService.CreateClaimAsync(request);

                LoadingPanel.Visibility = Visibility.Collapsed;

                MessageBox.Show($"Claim created successfully!\nClaim ID: {claim.ClaimId}",
                    "Success", MessageBoxButton.OK, MessageBoxImage.Information);

                DialogResult = true;
                this.Close();
            }
            catch (Exception ex)
            {
                LoadingPanel.Visibility = Visibility.Collapsed;
                IsEnabled = true;

                MessageBox.Show($"Error creating claim: {ex.Message}", "Error",
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            var result = MessageBox.Show("Are you sure you want to cancel? All data will be lost.",
                "Confirm Cancel", MessageBoxButton.YesNo, MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                DialogResult = false;
                this.Close();
            }
        }

        private string FormatFileSize(long bytes)
        {
            string[] sizes = { "B", "KB", "MB", "GB" };
            double len = bytes;
            int order = 0;
            while (len >= 1024 && order < sizes.Length - 1)
            {
                order++;
                len = len / 1024;
            }
            return $"{len:0.##} {sizes[order]}";
        }
    }

    public class ImageItem
    {
        public string FileName { get; set; } = string.Empty;
        public string FilePath { get; set; } = string.Empty;
        public string FileSize { get; set; } = string.Empty;
        public byte[] ImageData { get; set; } = Array.Empty<byte>();
        public BitmapImage? ThumbnailSource { get; set; }
    }
}
