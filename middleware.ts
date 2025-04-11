import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  const path = request.nextUrl.pathname;

  // Allow access to landing page, login, and signup without authentication
  if (path === "/" || path === "/login" || path === "/signup") {
    return response;
  }

  // Get token from cookies
  const token = request.cookies.get("token")?.value;
  const isLoggedIn = !!token;

  console.log(`Middleware: Path=${path}, IsLoggedIn=${isLoggedIn}`);

  // If user is not logged in and trying to access protected routes, redirect to login
  if (!isLoggedIn) {
    console.log("Middleware: No token found, redirecting to login");
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // If user is logged in
  if (isLoggedIn) {
    try {
      // Get user data from cookies
      const userData = request.cookies.get("user")?.value;
      if (userData) {
        const userDataObj = JSON.parse(userData);
        const hasMall = !!userDataObj.mall_id;
        
        console.log(`Middleware: User has mall=${hasMall}`);

        // If user has a mall and tries to access login/signup/mall-setup, redirect to dashboard
        if (hasMall && (path === "/login" || path === "/signup" || path === "/mall-setup")) {
          console.log("Middleware: User has mall, redirecting to dashboard");
          return NextResponse.redirect(new URL("/dashboard", request.url));
        }

        // If user doesn't have a mall and tries to access dashboard, redirect to mall-setup
        if (!hasMall && path === "/dashboard") {
          console.log("Middleware: User has no mall, redirecting to mall-setup");
          return NextResponse.redirect(new URL("/mall-setup", request.url));
        }
      } else {
        console.log("Middleware: No user data found in cookies");
      }
    } catch (error) {
      console.error("Error checking user data:", error);
      // In case of error, redirect to login
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  return response;
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}; 