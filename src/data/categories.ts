export interface CategoryCard {
  title: string;
  image: string;
  alt: string;
  links: { label: string; href: string }[];
}

export const heroQuickLinks = [
  { label: 'Inrichting', href: '/woonkamer/' },
  { label: 'Decor', href: '/decoratie/' },
  { label: 'Kunst', href: '/decoratie/' },
  { label: 'Gordijnen & Jaloezieën', href: '/woonkamer/' },
  { label: 'Sanitair', href: '/wasruimte/' },
  { label: 'Kinder meubelen', href: '/slaapruimte/' },
];

export const homepageCategories: CategoryCard[] = [
  {
    title: 'Bloemen',
    image: '/images/2023/05/bloemen.jpg',
    alt: 'Kleurrijk bloemenboeket voor interieurdecoratie',
    links: [
      { label: 'Krans', href: '/beste-krans/' },
      { label: 'Bloempot', href: '/beste-bloempot/' },
      { label: 'Kunstplant', href: '/beste-kunstplant/' },
      { label: 'Kunstbloem', href: '/beste-kunstbloem/' },
      { label: 'Droogboeket', href: '/beste-droogboeket/' },
    ],
  },
  {
    title: 'Kussen',
    image: '/images/2023/05/kussen-1024x1016.jpg',
    alt: 'Decoratieve kussens voor de woonkamer',
    links: [
      { label: 'Kussenvulling', href: '/beste-kussenvulling/' },
      { label: 'Binnenkussen', href: '/beste-binnenkussen/' },
      { label: 'Hoofdkussen', href: '/beste-hoofdkussen/' },
      { label: 'Kussenhoesje', href: '/beste-kussenhoesje/' },
      { label: 'Vloerkussen', href: '/beste-vloerkussen/' },
      { label: 'Stoelkussen', href: '/beste-stoelkussen/' },
      { label: 'Sierkussen', href: '/beste-sierkussen/' },
    ],
  },
  {
    title: 'Meubels',
    image: '/images/2023/05/meubels.jpg',
    alt: 'Stijlvolle meubels voor elke ruimte',
    links: [
      { label: 'Schoenenrek', href: '/beste-schoenenrek/' },
      { label: 'Boekenkast', href: '/beste-boekenkast/' },
      { label: 'Bijzettafel', href: '/beste-bijzettafel/' },
      { label: 'Tv meubel', href: '/beste-tv-meubel/' },
      { label: 'Stapelbed', href: '/beste-stapelbed/' },
      { label: 'Boxspring', href: '/beste-boxspring/' },
      { label: 'Slaapbank', href: '/beste-slaapbank/' },
      { label: 'Bartafel', href: '/beste-bartafel/' },
    ],
  },
  {
    title: 'Klokken',
    image: '/images/2023/05/klokken.jpg',
    alt: 'Klassieke en moderne klokken',
    links: [
      { label: 'Staande klok', href: '/beste-staande-klok/' },
      { label: 'Koekoeksklok', href: '/beste-koekoeksklok/' },
      { label: 'Projectieklok', href: '/beste-projectieklok/' },
      { label: 'Keukenklok', href: '/beste-keukenklok/' },
      { label: 'Wereldklok', href: '/beste-wereldklok/' },
      { label: 'Wandklok', href: '/beste-wandklok/' },
      { label: 'Tafelklok', href: '/beste-tafelklok/' },
    ],
  },
  {
    title: 'Spiegel',
    image: '/images/2023/05/spiegel.jpg',
    alt: 'Elegante spiegels voor interieur',
    links: [
      { label: 'Staande spiegel', href: '/beste-staande-spiegel/' },
      { label: 'Wandspiegel', href: '/beste-wandspiegel/' },
      { label: 'Plakspiegel', href: '/beste-plakspiegel/' },
      { label: 'Passpiegel', href: '/beste-passpiegel/' },
    ],
  },
  {
    title: 'Verlichting',
    image: '/images/2023/05/verlichting.jpg',
    alt: 'Sfeervolle verlichting voor thuis',
    links: [
      { label: 'Waxinelichthouder', href: '/beste-waxinelichthouder/' },
      { label: 'Kandelaar', href: '/beste-kandelaar/' },
      { label: 'Windlicht', href: '/beste-windlicht/' },
      { label: 'Lantaarn', href: '/beste-lantaarn/' },
      { label: 'Olielamp', href: '/beste-olielamp/' },
      { label: 'Kaars', href: '/beste-kaars/' },
    ],
  },
  {
    title: 'Wand Decoratie',
    image: '/images/2023/05/wanddecoratie.jpg',
    alt: 'Wanddecoratie voor een persoonlijk interieur',
    links: [
      { label: 'Decoratie ladder', href: '/beste-decoratie-ladder/' },
      { label: 'Dromenvanger', href: '/beste-dromenvanger/' },
      { label: 'Dierenhoofd', href: '/beste-dierenhoofd/' },
      { label: 'Spreuktegel', href: '/beste-spreuktegel/' },
      { label: 'Letterbord', href: '/beste-letterbord/' },
      { label: 'Wandkleed', href: '/beste-wandkleed/' },
      { label: 'Wandbord', href: '/beste-wandbord/' },
      { label: 'Tekstbord', href: '/beste-tekstbord/' },
      { label: 'Lightbox', href: '/beste-lightbox/' },
      { label: 'Letterbak', href: '/beste-letterbak/' },
      { label: 'Zuil', href: '/beste-zuil/' },
    ],
  },
  {
    title: 'Geur',
    image: '/images/2023/05/geur.jpg',
    alt: 'Geurproducten voor een aangename sfeer',
    links: [
      { label: 'Geurbrander', href: '/beste-geurbrander/' },
      { label: 'Geurzakje', href: '/beste-geurzakje/' },
      { label: 'Geurstokje', href: '/beste-geurstokje/' },
      { label: 'Wierook', href: '/beste-wierook/' },
    ],
  },
];

export const footerCategories = [
  {
    title: 'Klokken',
    links: [
      { label: 'Tafelklok', href: '/beste-tafelklok/' },
      { label: 'Wandklok', href: '/beste-wandklok/' },
      { label: 'Wereldklok', href: '/beste-wereldklok/' },
      { label: 'Keukenklok', href: '/beste-keukenklok/' },
      { label: 'Staande klok', href: '/beste-staande-klok/' },
      { label: 'Koekoeksklok', href: '/beste-koekoeksklok/' },
    ],
  },
  {
    title: 'Wasruimte',
    links: [
      { label: 'Dressboy', href: '/beste-dressboy/' },
      { label: 'Douchekop', href: '/beste-douchekop/' },
      { label: 'Kruimeldief', href: '/beste-kruimeldief/' },
      { label: 'Stoomreiniger', href: '/beste-stoomreiniger/' },
      { label: 'Kledingstomer', href: '/beste-kledingstomer/' },
      { label: 'Robotstofzuiger', href: '/beste-robotstofzuiger/' },
    ],
  },
  {
    title: 'Tuin',
    links: [
      { label: 'Krans', href: '/beste-krans/' },
      { label: 'Bartafel', href: '/beste-bartafel/' },
      { label: 'Bloempot', href: '/beste-bloempot/' },
      { label: 'Edelsteen', href: '/beste-edelsteen/' },
      { label: 'Hangstoel', href: '/beste-hangstoel/' },
      { label: 'Kunstplant', href: '/beste-kunstplant/' },
    ],
  },
  {
    title: 'Verlichting',
    links: [
      { label: 'Kaars', href: '/beste-kaars/' },
      { label: 'Lantaarn', href: '/beste-lantaarn/' },
      { label: 'Olielamp', href: '/beste-olielamp/' },
      { label: 'Windlicht', href: '/beste-windlicht/' },
      { label: 'Kandelaar', href: '/beste-kandelaar/' },
      { label: 'Kroonluchter', href: '/beste-kroonluchter/' },
    ],
  },
];

export const featuredReviews = [
  {
    category: 'Kunstplant',
    title: 'Scentchips®',
    excerpt:
      'Verwen je zintuigen met de Scentchips® Rib Round Bronze Wax Burner Geurbrander. Met deze unieke brander kun je je eigen geurcombinaties maken door te kiezen uit verschillende Scentchips.',
    href: '/beste-geurbrander/',
    image: '/images/2023/05/550x550-1.jpeg',
    alt: 'Scentchips geurbrander product',
  },
  {
    category: 'Dierenhoofd',
    title: 'Krans Kerst krans',
    excerpt:
      'Haal deze kerst de schoonheid van de natuur naar binnen met een authentieke Nobilis krans van Natural-Flowers.NL. Tinten van wintergroen zullen elk huis verlevendigen.',
    href: '/beste-krans/',
    image: '/images/2023/05/550x550.jpeg',
    alt: 'Kerst krans decoratie',
  },
  {
    category: 'Spreuktegel',
    title: 'Wijsheden tegeltje',
    excerpt:
      'Deze tegel is echt ideaal. Je kunt hem ophangen of neerzetten, want het haakje zit er gewoon bij. De spreuk kan voor iedereen van toepassing zijn.',
    href: '/beste-spreuktegel/',
    image: '/images/2023/05/550x733-225x300.jpeg',
    alt: 'Wijsheden spreuktegel',
  },
];
