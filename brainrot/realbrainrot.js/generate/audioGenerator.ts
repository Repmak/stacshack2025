import fetch from 'node-fetch';
import fs from 'fs';
import dotenv from 'dotenv';
dotenv.config();

// ElevenLabs API URL
const ELEVENLABS_API_URL = 'https://api.elevenlabs.io/v1/text-to-speech';

// Voice mapping - you'll need to replace these with actual ElevenLabs voice IDs
// Example voice IDs - replace with real ones from your ElevenLabs account
const VOICE_MAPPING = {
  'BARACK_OBAMA': 'CwhRBWXzGAHq8TQ4Fs17', // Replace with appropriate voice ID
  'JORDAN_PETERSON': 'IKne3meq5aSn9XLyUdCD', // Replace with appropriate voice ID
  // Add other voice mappings as needed
};

export async function generateAudio(
  voice_id: string,
  person: string,
  line: string,
  index: number
) {
  try {
    // Get the ElevenLabs voice ID from the mapping or use the provided voice_id
    const elevenLabsVoiceId = VOICE_MAPPING[person] || voice_id;

    console.log(`Generating audio for ${person} using voice ID: ${elevenLabsVoiceId}`);

    const response = await fetch(`${ELEVENLABS_API_URL}/${elevenLabsVoiceId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'xi-api-key': `${process.env.ELEVENLABS_API_KEY}`, // Make sure to add this to your .env file
      },
      body: JSON.stringify({
        text: line,
        model_id: 'eleven_monolingual_v1',
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75
        }
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Error response from ElevenLabs: ${errorText}`);
      throw new Error(`Server responded with status code ${response.status}: ${errorText}`);
    }

    // ElevenLabs returns the audio directly, not as JSON with base64
    const audioBuffer = await response.arrayBuffer();

    // Ensure the directory exists
    const dir = 'public/voice';
    if (!fs.existsSync(dir)){
      fs.mkdirSync(dir, { recursive: true });
    }

    // Write the buffer to a file
    fs.writeFileSync(`${dir}/${person}-${index}.mp3`, Buffer.from(audioBuffer));
    console.log(`Successfully saved audio for ${person}, line ${index}`);
    return Promise.resolve('Audio file saved successfully');
  } catch (error) {
    console.error(`Failed to generate audio for ${person}, line ${index}:`, error);
    throw error;
  }
}
