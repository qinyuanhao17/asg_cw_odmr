// SmncsShellTest.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include "../smncsftmt/smncsftmt.h"
#include <chrono>
#include <vector>
#include <iostream>
#include <thread>
#include <windows.h>
#include <fstream>

void exit_program()
{
	std::cout << "Press Any Key to Exit" << std::endl;
	char a;
	std::cin >> a;
}


int main()
{

		int nTaskRunMode = FTMT_TASK_RUN_MODE_ITTR_T;

		int ittr_intvl = 100;

		float statistics_time = 1;

		std::vector<int> devids = { 0 };

		if (SetStatisticsTime(nTaskRunMode, statistics_time) != FTMT_ERROR_NONE)//统计时间10s   
		{
			std::cerr << "SetStatisticsTime Error" << std::endl;
			exit_program();
		}

		if (SetFileMode(nTaskRunMode, FTMT_FILE_SAVE_MODE_BIN, FTMT_FILE_SERIES_MODE_EACH) != FTMT_ERROR_NONE)
		{
			std::cerr << "SetFileMode Error" << std::endl;
			exit_program();
		}

		int connected_devs = 0;
		char dev[256];
		GetDevType(0, dev);

		for (int devid = 0; devid < 3;devid++)
		{

			if (!USBConnected(devid)) //set devid
			{
				continue;
			}
			connected_devs++;

			unsigned __int8 mask8 = CH_MASK_0;
			if (EnableITTR(devid, FTMT_BOARD_A, mask8) != FTMT_ERROR_NONE)//BOARD A, CHANNEL 0  
			{
				std::cerr << "EnableITTR Error" << std::endl;
				exit_program();
			}

			if (SetStartFreqDiv(devid, FTMT_START_FREQ_DIV_2) != FTMT_ERROR_NONE) //Frequency Division:1   
			{
				std::cerr << "SetStartFreqDiv Error" << std::endl;
				exit_program();
			}

			if (SetITTRInterval(devid, FTMT_BOARD_A, ittr_intvl) != FTMT_ERROR_NONE)
			{
				std::cerr << "SetITTRInterval Error" << std::endl;
				exit_program();
			}

			if (SetFilePath(devid, nTaskRunMode, "D:\\siminics") != FTMT_ERROR_NONE)
			{
				std::cerr << "SetFilePath Error" << std::endl;
				exit_program();
			}

			if (SetBlockedWindow(devid, 0) != FTMT_ERROR_NONE)
			{
				std::cerr << "SetBlockedWindow Error" << std::endl;
				exit_program();

			}

			if (SetITTREndMode(FTMT_ITTR_END_MODE_TIME) != FTMT_ERROR_NONE) //用户停止，非自动停止
			//if (SetITTREndMode(FTMT_TTTR_END_MODE_EVENT, 1000000) != FTMT_ERROR_NONE) //用户停止，非自动停止
			{
				std::cerr << "SetITTREndMode Error" << std::endl;
				exit_program();
			}


		}

		if (connected_devs == 0)
		{
			std::cerr << "No Connected Devs" << std::endl;
			exit_program();
		}

		if (SetMemoryDataMode(true) != FTMT_ERROR_NONE)
		{
			std::cerr << "SetMemoryDataMode Error" << std::endl;
			exit_program();
		}

		if (!MemoryDataModeEnabled())
		{
			std::cerr << "MemoryDataModeEnabled Error" << std::endl;
			exit_program();
		}

		for (int loops = 0; loops < 10; loops++)
		{

			auto ittr_start_time = std::chrono::system_clock::now();
			if (StartTask(nTaskRunMode) != FTMT_ERROR_NONE)//StartTask ITTR_T
			{
				std::cerr << "StartTask Error" << std::endl;
				continue;
			}

			auto start_end_time = std::chrono::system_clock::now();

			//static int nIndex = 0;
			FILE* fp = nullptr;
			std::string strIndex = "D:\\siminics\\ITTR.dat";
			fopen_s(&fp, strIndex.c_str(), "wb");
			while (!IsTaskCompleted()) {
				FtmtRawData* dat_ptr = GetMemoryData(0);
				if (dat_ptr)
				{
					if (nullptr != fp)
					{
						fwrite(dat_ptr->dptr, 1, dat_ptr->dlen, fp);
					}

					ReleaseMemoryData(dat_ptr);
				}
			}

			if (fp)
			{
				fclose(fp);
				fp = nullptr;
			}

			auto task_end_time = std::chrono::system_clock::now();


			auto start_elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(start_end_time - ittr_start_time);

			auto task_elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(task_end_time - ittr_start_time);


			std::cout << "StartTask Consumed: " << start_elapsed.count() << "    Total time: " << task_elapsed.count() << std::endl;

			//std::this_thread::sleep_for(std::chrono::milliseconds(100));

		}

	exit_program();
	
    return 0;
}

