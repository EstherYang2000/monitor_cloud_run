
import subprocess
def scale_up_mem():
    print("Auto scale up memory to 512Mi.")
    command = "gcloud run services update hedgedoc --platform=managed --memory=512Mi --project=tsmccareerhack2024-icsd-grp2 --region=us-central1"
    # 使用 subprocess.Popen() 创建进程
    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 提供需要的输入，以换行符 \n 结束
    input_data = "your_input_value\n"
    process.stdin.write(input_data)
    process.stdin.flush()  # 刷新输入流

    # 获取输出和错误信息
    output, error = process.communicate()

    # 检查返回码
    return_code = process.returncode
    if return_code == 0:
        print("Command executed successfully.")
    else:
        print(f"Error executing command. Return code: {return_code}")
        print("Error message:")
        print(error)
    # result = subprocess.run(command, shell=True, check=True, text=True)


# 使用 subprocess.run() 執行指令


def scale_up_cpu():
    print("Auto scale up CPU to 2.")
    command = "gcloud run services update hedgedoc --platform=managed --cpu=2 --project=tsmccareerhack2024-icsd-grp2 --region=us-central1"
    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 提供需要的输入，以换行符 \n 结束
    input_data = "your_input_value\n"
    process.stdin.write(input_data)
    process.stdin.flush()  # 刷新输入流

    # 获取输出和错误信息
    output, error = process.communicate()

    # 检查返回码
    return_code = process.returncode
    if return_code == 0:
        print("Command executed successfully.")
    else:
        print(f"Error executing command. Return code: {return_code}")
        print("Error message:")
        print(error)
