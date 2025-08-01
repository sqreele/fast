import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const error = searchParams.get('error');
  
  const errorMessages: Record<string, string> = {
    Configuration: 'There was a problem with the server configuration.',
    AccessDenied: 'Access denied. You do not have permission to access this resource.',
    Verification: 'The verification token is invalid or has expired.',
    Default: 'An error occurred during authentication.'
  };
  
  const message = errorMessages[error || 'Default'] || errorMessages.Default;
  
  return NextResponse.json({
    error: error || 'Default',
    message,
    timestamp: new Date().toISOString()
  });
}

export async function POST() {
  return NextResponse.json({
    error: 'MethodNotAllowed',
    message: 'POST method not allowed for error endpoint'
  }, { status: 405 });
}