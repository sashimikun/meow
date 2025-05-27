// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Screenshot API Service Docs',
  tagline: 'Comprehensive documentation for the Screenshot API Service',
  favicon: 'img/favicon.ico', // Default, can be changed later

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://sashimikun.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/meow/',

  // GitHub pages deployment config.
  organizationName: 'sashimikun', // Usually your GitHub org/user name.
  projectName: 'meow', // Usually your repo name.

  onBrokenLinks: 'warn', // Changed from 'throw'
  onBrokenMarkdownLinks: 'warn', // Changed from 'warn' (no change, but specified)

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
            'https://github.com/sashimikun/meow/edit/main/docs/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          editUrl:
            'https://github.com/sashimikun/meow/edit/main/docs/blog/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg', // Default, can be changed
      navbar: {
        title: 'Screenshot API Service', // Updated
        logo: {
          alt: 'My Site Logo', // Default
          src: 'img/logo.svg',   // Default
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'mySidebar', // Updated to use 'mySidebar'
            position: 'left',
            label: 'Docs', // Updated
          },
          {to: '/blog', label: 'Blog', position: 'left'}, // Kept default
          {
            href: 'https://github.com/sashimikun/meow', // Updated
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Documentation', // Updated label
                to: '/docs/introduction', // Updated path
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Stack Overflow',
                href: 'https://stackoverflow.com/questions/tagged/docusaurus',
              },
              {
                label: 'Discord',
                href: 'https://discordapp.com/invite/docusaurus',
              },
              {
                label: 'X',
                href: 'https://x.com/docusaurus',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/sashimikun/meow', // Updated to project repo
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Screenshot API Service. Built with Docusaurus.`, // Updated
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
