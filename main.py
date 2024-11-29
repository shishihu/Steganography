import argparse
import cv2

# Location in a pixel where the value is written to
writtenIndex = -3
# Number of bits of a char
charLength = 9
# Number of times to write each character
redundantCharCopies = 135*3

def writeCharToIm(pixelArray, character, i):
    width = len(pixelArray)
    for j in range(charLength):
        for l in range(redundantCharCopies//3):
            # Get pixel array
            pixel = pixelArray[(charLength*i*redundantCharCopies//3 + j*redundantCharCopies//3 + l) // width, (charLength*i*redundantCharCopies//3 + j*redundantCharCopies//3 + l) % width]
            for k in range(3):
                # Binary of RGB values of the pixel
                rgbValue = bin(pixel[k])[2:].zfill(charLength)
                # Replace the written index of the RGB values with the bit of the character to be written
                pixel[k] = int(rgbValue[:writtenIndex] + character[j] + (rgbValue[writtenIndex + 1:] if writtenIndex < -1 else ""), 2)
            # Replace the RGB value of pixel with modified RGB values
            pixelArray[(charLength*i*redundantCharCopies//3 + j*redundantCharCopies//3 + l) // width, (charLength*i*redundantCharCopies//3 + j*redundantCharCopies//3 + l) % width] = pixel


def embed(inputImage, outputImage, message):
    try:
        # get a matrix of RGB values of the image
        pixelArray = cv2.imread(inputImage)
        for i in range(len(message)):
            # gets the binary of the ASCII of the character
            character = bin(ord(message[i]))[2:].zfill(charLength)
            writeCharToIm(pixelArray, character, i)

        # end of message characters
        writeCharToIm(pixelArray, '000000000', len(message))
        writeCharToIm(pixelArray, '000000000', len(message) + 1)
        writeCharToIm(pixelArray, '000000000', len(message) + 2)
        writeCharToIm(pixelArray, '000000000', len(message) + 3)
        cv2.imwrite(outputImage, pixelArray)
        print("Embedding was successful. Please check your image: " + outputImage + ". ")
    except:
        print("Embedding was not successful. Please try again.")

def readCharacter(pixelArray, i):
    # 000, 001, 010, 100 maps to 0
    # 011, 110, 101, 111 maps to 1

    width = len(pixelArray)
    message = ""
    for j in range(charLength):
        # Determines amount of ones in the binary character
        onesCount = 0
        for l in range(redundantCharCopies//3):
            # get pixel to read
            pixel = pixelArray[(charLength*i*redundantCharCopies//3 + j*redundantCharCopies//3 + l) // width, (charLength*i*redundantCharCopies//3 + j*redundantCharCopies//3 + l) % width]
            for k in range(3):
                # Check if wrote 1 or 0
                if bin(pixel[k]).zfill(charLength)[writtenIndex] == "1":
                    onesCount += 1
        # Add 1 or 0 to message
        if onesCount > redundantCharCopies//2:
            message += "1"
        else:
            message += "0"
    # Returns character by getting the int from binary and modding by 128 to keep it in ASCII bounds
    return chr(int(message, 2) % 128)


def decode(image):
    try:
        pixelArray = cv2.imread(image)
        # index of current character
        i = 0
        message = ""
        # check number of ending characters
        numEndChars = 0
        while True:
            character = readCharacter(pixelArray, i)
            i += 1
            # Count number of ending characters
            if character == "\0":
                numEndChars += 1
            else:
                numEndChars = 0
            # If ending character count = 2, break
            if numEndChars == 2:
                break
            # Add character to message string
            message += character
        # Print message
        print("The decoded message is: " + message)
    except:
        # If something goes wrong
        print("Decoding was not successful. Please try again.")


def getInput():
    # Use the argparse library to get input
    parser = argparse.ArgumentParser(
        prog='Steganography Program',
        description='Embed or decode an image',
        epilog='Your program has finished running.'
    )
    # add parsers
    global_parser = argparse.ArgumentParser(prog="Steganography Program")
    subparsers = global_parser.add_subparsers(
        title="subcommands", help="other"
    )

    # Define embed parser
    embed_parser = subparsers.add_parser("embed", help="Embed an image with a message")
    embed_parser.add_argument(dest="operands", type=str, nargs=3, help="Enter a command in the form \"embed "
                                                                "<input_image> <output_image> <message>\"")
    embed_parser.set_defaults(func=embed)

    # Define decode parser
    decode_parser = subparsers.add_parser("decode", help="Decode an image")
    decode_parser.add_argument(dest="operands", type=str, nargs=1, help="Enter a command in the form \"decode "
                                                                        "<input_image>\"")
    decode_parser.set_defaults(func=decode)

    # Parse arguments
    args = global_parser.parse_args()
    args.func(*args.operands)


getInput()
#embed("image.jpeg", "testoutput.jpeg", "skibidi toilet"*100)
#decode("ouput.jpeg")
