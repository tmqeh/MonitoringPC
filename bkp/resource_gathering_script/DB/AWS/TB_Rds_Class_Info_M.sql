USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Rds_Class_Info_M]    Script Date: 2022-02-11 ¿ÀÀü 9:34:45 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Rds_Class_Info_M](
	[ServerClass] [varchar](30) NOT NULL,
	[vCPU] [int] NULL,
	[ECU] [varchar](30) NULL,
	[Memory_GB] [decimal](10, 2) NULL,
	[VPC_Only] [varchar](3) NULL,
	[EBS_Optimized] [varchar](3) NULL,
	[Max_Bandwidth_Mbps] [varchar](30) NULL,
	[Network_Performance] [varchar](30) NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_Rds_Class_Info_M] PRIMARY KEY CLUSTERED 
(
	[ServerClass] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


