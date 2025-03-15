/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [
      'picsum.photos',
      'placehold.co',
      'i.ebayimg.com',
      'i.etsystatic.com',
      'www.hippostcard.com',
      'example.com',
      'dummyimage.com',
      'picsum.photos'
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    dangerouslyAllowSVG: true,
    contentDispositionType: 'attachment',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  experimental: {
    serverExternalPackages: []
  },
};

module.exports = nextConfig;
