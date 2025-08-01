import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  // Return a simple HTML page for signout confirmation
  const html = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Sign Out</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          margin: 0;
          padding: 0;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: #f9fafb;
        }
        .container {
          max-width: 400px;
          padding: 2rem;
          background: white;
          border-radius: 8px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          text-align: center;
        }
        h1 {
          color: #059669;
          margin-bottom: 1rem;
        }
        p {
          color: #6b7280;
          margin-bottom: 2rem;
        }
        .button {
          display: inline-block;
          padding: 0.75rem 1.5rem;
          margin: 0.5rem;
          text-decoration: none;
          border-radius: 6px;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        .button-primary {
          background-color: #4f46e5;
          color: white;
        }
        .button-primary:hover {
          background-color: #4338ca;
        }
        .button-secondary {
          background-color: #f3f4f6;
          color: #374151;
          border: 1px solid #d1d5db;
        }
        .button-secondary:hover {
          background-color: #e5e7eb;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>Successfully Signed Out</h1>
        <p>You have been successfully signed out of your account.</p>
        <a href="/signin" class="button button-primary">Sign In Again</a>
        <a href="/" class="button button-secondary">Go Home</a>
      </div>
    </body>
    </html>
  `;

  return new NextResponse(html, {
    headers: {
      'Content-Type': 'text/html',
    },
  });

}

export async function POST(request: NextRequest) {
  // Handle POST requests for signout (redirect directly to signin page)
  return NextResponse.redirect(new URL('/signin', request.url));
}