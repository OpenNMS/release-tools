import json, os, shutil, datetime


def backup_save(filename, data, folder=""):
    if not os.path.exists("workspace/backups"):
        os.mkdir("workspace/backups")

    if not os.path.exists("workspace/backups/" + filename.split(".json")[0]):
        os.mkdir("workspace/backups/" + filename.split(".json")[0])

    outputPath = "workspace/" + filename

    if folder:
        outputPath = "workspace/" + folder
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)
        outputPath = "workspace/" + folder + "/" + filename

    if os.path.exists(outputPath):
        print("<<", "backup_save", ">>", "Path", outputPath, "exists")

        with open(outputPath, "r") as f:
            _tmpdata = json.load(f)
        _backupdate = (
            _tmpdata["datetime"].replace(" ", "__").replace(":", "-").replace(".", "_")
        )
        print(
            "Moving old branch data to",
            "workspace/backups/"
            + filename.split(".json")[0]
            + "/"
            + filename
            + "__"
            + _backupdate
            + ".json",
        )
        shutil.move(
            outputPath,
            "workspace/backups/"
            + filename.split(".json")[0]
            + "/"
            + filename.split(".json")[0]
            + "__"
            + _backupdate
            + ".json",
        )
    with open(outputPath, "w") as f:
        json.dump(data, f, indent=4)

    print("Created file", outputPath)
