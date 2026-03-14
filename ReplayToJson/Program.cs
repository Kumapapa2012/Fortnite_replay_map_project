using FortniteReplayReader;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Unicode;
using Unreal.Core.Models.Enums;

if (args.Length < 1)
{
    Console.Error.WriteLine("Usage: ReplayToJson <INPUT_REPLAY_FILE> [OUTPUT_JSON_FILE]");
    return 1;
}

var inputPath = args[0];
if (!File.Exists(inputPath))
{
    Console.Error.WriteLine($"Error: File not found: {inputPath}");
    return 1;
}

var outputPath = args.Length >= 2
    ? args[1]
    : Path.Combine(Directory.GetCurrentDirectory(), Path.GetFileNameWithoutExtension(inputPath) + ".json");

try
{
    var reader = new ReplayReader(parseMode: ParseMode.Full);
    var replay = reader.ReadReplay(inputPath);

    var options = new JsonSerializerOptions
    {
        Encoder = JavaScriptEncoder.Create(UnicodeRanges.All),
        NumberHandling = System.Text.Json.Serialization.JsonNumberHandling.AllowNamedFloatingPointLiterals,
        WriteIndented = true
    };

    var json = JsonSerializer.Serialize(replay, options);
    await File.WriteAllTextAsync(outputPath, json, System.Text.Encoding.UTF8);

    Console.WriteLine(outputPath);
    return 0;
}
catch (Exception ex)
{
    Console.Error.WriteLine($"Error: {ex.Message}");
    return 1;
}
