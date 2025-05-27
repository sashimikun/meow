import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Screenshot API Service',
  tagline: 'Capture Webpages with Ease',
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

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts', // Adjusted from require.resolve
          // Please change this to your repo.
          editUrl:
            'https://github.com/sashimikun/meow/tree/main/docs/',
        },
        blog: false, // Disabled blog as per instructions
        // blog: {
        //   showReadingTime: true,
        //   feedOptions: {
        //     type: ['rss', 'atom'],
        //     xslt: true,
        //   },
        //   editUrl:
        //     'https://github.com/sashimikun/meow/tree/main/docs/blog/',
        //   onInlineTags: 'warn',
        //   onInlineAuthors: 'warn',
        //   onUntruncatedBlogPosts: 'warn',
        // },
        theme: {
          customCss: './src/css/custom.css', // Adjusted from require.resolve
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg', // Default, can be changed later
    navbar: {
      title: 'Screenshot API Service',
      logo: {
        alt: 'Screenshot API Service Logo',
        src: 'img/logo.svg', // Default, can be changed later
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar', // This ID should match one in sidebars.ts
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/sashimikun/meow',
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
              label: 'Introduction',
              to: '/docs/introduction',
            },
            {
              label: 'API Reference',
              to: '/docs/api-reference',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub Issues',
              href: 'https://github.com/sashimikun/meow/issues',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/sashimikun/meow',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Screenshot API Service. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
