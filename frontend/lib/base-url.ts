export const base_usrl = (
  process.env.NEXT_PUBLIC_API_URL?.trim() ||
  "https://front-a8efgycrdeh0a8ht.uaenorth-01.azurewebsites.net"
).replace(/\/+$/, "");

