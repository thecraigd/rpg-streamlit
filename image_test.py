from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64



client = genai.Client()

contents = ('Hi, please create a sci-fi image in widescreen cinematic format and 5:2 aspect ration, depicting the Nexus Market, a cacophony of sights and sounds. Vendor stalls overflow with shimmering artifacts, bioluminescent fruits, and strange technologies from across the Nexus. Human-plant hybrids, their bodies adorned with leaves and glowing blossoms, mingle with chrome-plated cyborgs and flickering digital entities. Fortified walls of woven vines and reinforced steel rise around the town, a testament to the constant need for security in this volatile corner of the galaxy.')

response = client.models.generate_content(
    model="gemini-2.0-flash-exp-image-generation",
    contents=contents,
    config=types.GenerateContentConfig(
      response_modalities=['Text', 'Image']
    )
)

for part in response.candidates[0].content.parts:
  if part.text is not None:
    print(part.text)
  elif part.inline_data is not None:
    image_data = part.inline_data.data
    if isinstance(image_data, str):
      image_data = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_data))
    image.save('gemini-native-image.png')
    image.show()
