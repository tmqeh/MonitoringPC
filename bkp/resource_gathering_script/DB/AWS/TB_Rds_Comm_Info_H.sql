USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Rds_Comm_Info_H]    Script Date: 2022-02-11 ¿ÀÀü 9:34:50 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Rds_Comm_Info_H](
	[REG_DT] [varchar](8) NOT NULL,
	[ServerHost] [varchar](50) NOT NULL,
	[ServerClass] [varchar](30) NULL,
	[ServerName] [varchar](100) NULL,
	[VPC] [varchar](30) NULL,
	[Storage_Type] [varchar](30) NULL,
	[Storage_Size_GB] [int] NULL,
	[iops] [int] NULL,
	[Status] [varchar](30) NULL,
	[VPC_Zone] [varchar](30) NULL,
	[DBMS_Type] [varchar](30) NULL,
	[DBMS_Version] [varchar](30) NULL,
	[Log_List] [varchar](50) NULL,
	[Mon_Interval] [int] NULL,
	[MultiAZ_YN] [varchar](1) NULL,
	[Perf_Insight_YN] [varchar](1) NULL,
	[Auto_Ver_Upgrade_YN] [varchar](1) NULL,
	[Public_Access_YN] [varchar](1) NULL,
	[Del_Protect_YN] [varchar](1) NULL,
	[Use_YN] [varchar](1) NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_Rds_Comm_Info_H] PRIMARY KEY CLUSTERED 
(
	[REG_DT] ASC,
	[ServerHost] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[TB_Rds_Comm_Info_H] ADD  DEFAULT (CONVERT([varchar],getdate(),(112))) FOR [REG_DT]
GO


