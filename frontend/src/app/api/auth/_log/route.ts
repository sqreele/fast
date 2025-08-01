import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Log authentication events
    console.log('Auth event:', {
      timestamp: new Date().toISOString(),
      level: body.level || 'info',
      message: body.message || 'Auth event',
      code: body.code || 'unknown',
      type: body.type || 'auth'
    });
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Auth log error:', error);
    return NextResponse.json(
      { error: 'Failed to log auth event' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({ message: 'Auth logging endpoint' });
}