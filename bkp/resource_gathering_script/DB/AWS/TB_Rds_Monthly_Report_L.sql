USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Rds_Monthly_Report_L]    Script Date: 2022-02-11 ¿ÀÀü 9:35:14 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Rds_Monthly_Report_L](
	[CollectDT] [varchar](8) NOT NULL,
	[CollectHH] [varchar](2) NOT NULL,
	[ServerHost] [varchar](30) NOT NULL,
	[CPU_PCT] [decimal](15, 2) NOT NULL,
	[Storage_TOT_GB] [int] NULL,
	[Storage_Free_GB] [int] NULL,
	[Storage_Use_GB] [int] NULL,
	[Storage_Used_PCT] [decimal](10, 2) NULL,
	[MEM_TOT_GB] [decimal](10, 2) NULL,
	[MEM_Free_GB] [int] NULL,
	[MEM_Use_GB] [decimal](13, 2) NULL,
	[MEM_Used_PCT] [decimal](10, 2) NULL,
	[Read_IOPS] [decimal](15, 2) NULL,
	[Write_IOPS] [decimal](15, 2) NULL,
	[TOT_IOPS] [decimal](16, 2) NULL,
 CONSTRAINT [PK_Rds_Monthly_Report_L] PRIMARY KEY CLUSTERED 
(
	[CollectDT] ASC,
	[CollectHH] ASC,
	[ServerHost] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


