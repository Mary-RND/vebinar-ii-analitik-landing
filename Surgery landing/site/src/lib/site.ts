export const site = {
  brandName: "Пластический хирург",
  tagline: "Проводник в разговоре с вашим телом",
  phone: "+7 (000) 000-00-00",
  phoneHref: "tel:+70000000000",
  telegram: "@doctor_username",
  whatsapp: "+7 (000) 000-00-00",
  email: "hello@example.ru",
  address: "Москва, ул. Клиническая, 10",
  workHours: "Ежедневно с 09:00 до 21:00. Мы на связи.",
};

export const services = {
  face: {
    title: "Пластика лица",
    slug: "/napravleniya/plastika-lica",
    items: ["Ринопластика", "Блефаропластика", "Ритидэктомия"],
  },
  body: {
    title: "Пластика тела",
    slug: "/napravleniya/plastika-tela",
    items: ["Маммопластика", "Абдоминопластика", "Липосакция и контурирование"],
  },
  postpartum: {
    title: "Послеродовое восстановление",
    slug: "/poslerodovoe-vosstanovlenie",
    items: ["Восстановление живота", "Работа с грудью", "Тонус и рельеф"],
  },
  maleBody: {
    title: "Мужская пластика",
    slug: "/muzhskaya-plastika",
    items: ["Гинекомастия", "Абдоминопластика", "Липосакция и контурирование"],
  },
};

export const femaleBodyZones = [
  { id: "breasts", label: "Маммопластика", hint: "Грудь" },
  { id: "belly", label: "Абдоминопластика", hint: "Живот" },
  { id: "hips", label: "Липосакция и подтяжка", hint: "Бёдра" },
  { id: "buttocks", label: "Подтяжка ягодиц", hint: "Ягодицы" },
  { id: "arms", label: "Брахиопластика", hint: "Руки" },
  { id: "face", label: "Ритидэктомия и блефаропластика", hint: "Лицо" },
];

export const maleBodyZones = [
  { id: "chest", label: "Гинекомастия", hint: "Грудь" },
  { id: "belly", label: "Абдоминопластика", hint: "Живот" },
  { id: "back", label: "Липосакция и контурирование", hint: "Спина" },
  { id: "face", label: "Пластика лица и шеи", hint: "Лицо" },
  { id: "neck", label: "Пластика лица и шеи", hint: "Шея" },
];