using System;

namespace VendorWarrantyManager.Models
{
    public class WarrantyInfo
    {
        public string ServiceTag { get; set; } = string.Empty;
        public string ProductName { get; set; } = string.Empty;
        public DateTime? StartDate { get; set; }
        public DateTime? EndDate { get; set; }
        public string Status { get; set; } = string.Empty;
        public bool IsValid { get; set; }
        public string? ServiceLevel { get; set; }
    }
}
