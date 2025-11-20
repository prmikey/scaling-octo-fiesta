using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using VendorWarrantyManager.Services;

namespace VendorWarrantyManager
{
    public partial class App : Application
    {
        public static ServiceProvider? ServiceProvider { get; private set; }

        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            var serviceCollection = new ServiceCollection();
            ConfigureServices(serviceCollection);
            ServiceProvider = serviceCollection.BuildServiceProvider();
        }

        private void ConfigureServices(IServiceCollection services)
        {
            // Register HttpClient for each vendor
            services.AddHttpClient<DellApiService>();
            services.AddHttpClient<LenovoApiService>();

            // Register services
            services.AddTransient<DellApiService>();
            services.AddTransient<LenovoApiService>();
        }

        protected override void OnExit(ExitEventArgs e)
        {
            ServiceProvider?.Dispose();
            base.OnExit(e);
        }
    }
}
