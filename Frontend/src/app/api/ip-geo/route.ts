import { NextResponse } from "next/server";

export async function GET() {
  try {
    const res = await fetch("http://ip-api.com/json/");
    if (!res.ok) {
      return NextResponse.json({ error: "ip-api failed" }, { status: res.status });
    }
    const data = await res.json();
    if (data.status !== "success") {
      return NextResponse.json({ error: data.message }, { status: 400 });
    }
    return NextResponse.json({
      city: data.city,
      state: data.regionName,
      country: data.country,
    });
  } catch (error) {
    return NextResponse.json({ error: "Proxy server error" }, { status: 500 });
  }
}
